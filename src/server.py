import geoip2.database
import math
import socket
from haversine import haversine # type: ignore
from lib import DnsQueryPacket, build_dns_response, build_refused_response
from typing import NamedTuple, Tuple

HOST = "127.0.0.1"
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


FAKE_CLIENT_IP = "44.184.98.219"
FAKE_EDGE_SERVER_IPS = [
    "3.204.143.48",
    "28.170.247.194",
    "32.197.80.200",
    "5.20.98.162"
    ]

class EdgeServer(NamedTuple):
    ip: str
    coords: Tuple[float, float]

def get_ip_coords(ip_addr: str, db_reader: geoip2.database.Reader) -> Tuple[float, float]:
    response = db_reader.city(ip_addr)
    if (not response.location.latitude) or (not response.location.longitude):
        raise Exception(f"Failed to retrieve coordinates for IP address {ip_addr}")
    return (response.location.latitude, response.location.longitude) 

def find_closest_server(client_coords: Tuple[float, float], edge_servers: list[EdgeServer]) -> str:
    closest_server_ip = "" 
    minimum_distance = math.inf 
    for server in edge_servers:
        distance = haversine(client_coords, server.coords)
        if distance < minimum_distance: 
            closest_server_ip = server.ip 
            minimum_distance = distance

    return closest_server_ip 
    

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((HOST, PORT))
    reader = geoip2.database.Reader('../data/GeoLite2-City.mmdb')
    edge_servers = [EdgeServer(ip, get_ip_coords(ip, reader)) for ip in FAKE_EDGE_SERVER_IPS]

    while True:
        data, (client_ip, client_port) = sock.recvfrom(512)
        try: 
            query_packet = DnsQueryPacket(data)
        except Exception: # don't respond if we receive malformed or non-DNS traffic
            continue

        # Refuse any queries other than those for an A record
        if query_packet.question.record_type != 1:
            response_packet = build_refused_response(query_packet) 
            sock.sendto(response_packet, (client_ip, client_port))
            continue

        try:
            client_coords = get_ip_coords(FAKE_CLIENT_IP, reader)
            closest_server_ip = find_closest_server(client_coords, edge_servers)
        except Exception as e:
            print(f"Error while finding closest server for client {client_ip}: {e}")
            closest_server_ip = edge_servers[0].ip

        response_packet = build_dns_response(query_packet, closest_server_ip, 50)
        print(response_packet)
        sock.sendto(response_packet, (client_ip, client_port))





        




