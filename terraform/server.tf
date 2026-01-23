resource "digitalocean_droplet" "origin_server" {
    image = "ubuntu-24-04-x64"
    name = "origin-server"
    region = "syd1"
    size = "s-1vcpu-1gb"
    ssh_keys = [
        data.digitalocean_ssh_key.toy_cdn.id
    ]

    connection {
      host = self.ipv4_address
      user = "root"
      type = "ssh"
      agent = true
    }
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

    connection {
      host = self.ipv4_address
      user = "root"
      type = "ssh"
      agent = true
    }
}

resource "digitalocean_droplet" "nameserver" {
    image = "ubuntu-24-04-x64"
    name = "nameserver"
    region = "sfo3"
    size = "s-1vcpu-1gb"
    ssh_keys = [
        data.digitalocean_ssh_key.toy_cdn.id
    ]

    connection {
      host = self.ipv4_address
      user = "root"
      type = "ssh"
      agent = true
    }

    provisioner "file" {
        content = jsonencode({
            origin_ip = digitalocean_droplet.origin_server.ipv4_address
            edge_server_ips = [for v in digitalocean_droplet.edge_servers: v.ipv4_address]
        })
        destination = "/opt/config.json"
    }

    provisioner "remote-exec" {
        inline = [
            "cloud-init status --wait || true", # apparently I need this to keep terraform from killing itself
            "apt-get update && apt-get install -y docker.io",
            "docker run -d -p 53:53/udp -v /opt/config.json:/app/data/config.json aydinschwa/nameserver:latest"
        ]
    }
}