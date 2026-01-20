import socket

from lib import build_dns_packet

HOST = "127.0.0.1"
PORT = 65433  # Port to listen on (non-privileged ports are > 1023)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        domain_name = "google.com"
        dns_packet = build_dns_packet(domain_name) 
        s.sendto(dns_packet, (HOST, PORT - 1))
