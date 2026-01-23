resource "digitalocean_droplet" "origin_server" {
    image = "ubuntu-24-04-x64"
    name = "asap-site-server"
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
}

output "origin_server_ip" {
    value = digitalocean_droplet.origin_server.ipv4_address
}

