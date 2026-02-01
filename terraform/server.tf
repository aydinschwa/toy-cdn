resource "digitalocean_droplet" "origin_server" {
    image = "ubuntu-24-04-x64"
    name = "origin-server"
    region = "syd1"
    size = "s-1vcpu-1gb"
    ssh_keys = [
        data.digitalocean_ssh_key.toy_cdn.id
    ]
    user_data = file("${path.module}/cloud-init-origin.yaml")
}

variable "edge_server_regions" {
  type = set(string)
  default = ["sfo3"]
}

resource "digitalocean_droplet" "edge_servers" {
    for_each = var.edge_server_regions
    image = "ubuntu-24-04-x64"
    name = "edge-server-${each.value}"
    region = "${each.value}"
    size = "s-1vcpu-1gb"
    ssh_keys = [
        data.digitalocean_ssh_key.toy_cdn.id
    ]
    user_data = templatefile("${path.module}/cloud-init-edge.yaml", {
        origin_ip = digitalocean_droplet.origin_server.ipv4_address
    })
}

resource "digitalocean_droplet" "nameserver" {
    image = "ubuntu-24-04-x64"
    name = "nameserver"
    region = "sfo3"
    size = "s-1vcpu-1gb"
    ssh_keys = [
        data.digitalocean_ssh_key.toy_cdn.id
    ]

    user_data = templatefile("${path.module}/cloud-init-nameserver.yaml", {
        config_json_content = jsonencode({
            origin_ip = digitalocean_droplet.origin_server.ipv4_address
            edge_server_ips = [for v in digitalocean_droplet.edge_servers: v.ipv4_address]
        })
    })

}