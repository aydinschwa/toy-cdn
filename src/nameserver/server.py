import geoip2.database
import json
import math
import socket
from haversine import haversine # type: ignore
from lib import DnsQueryPacket, build_dns_response, build_refused_response
from typing import NamedTuple, Tuple

HOST = "0.0.0.0"
PORT = 53  # standard DNS port


with open("config.json", "r") as f:
    config = json.load(f)
    EDGE_SERVER_IPS = config["edge_server_ips"] 
    ORIGIN_IP = config["origin_ip"]

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
    reader = geoip2.database.Reader('data/GeoLite2-City.mmdb')
    edge_servers = [EdgeServer(ip, get_ip_coords(ip, reader)) for ip in EDGE_SERVER_IPS]

    while True:
        data, (client_ip, client_port) = sock.recvfrom(512)
        try: 
            query_packet = DnsQueryPacket(data)
        except Exception: # don't respond if we receive malformed or non-DNS traffic
            continue

        # refuse any queries other than those for an A record
        # refuse any queries for a random domain I don't own
        if (query_packet.question.record_type != 1) or \
           (not query_packet.question.domain_name.endswith("cdn-test.space")):
            response_packet = build_refused_response(query_packet) 
            sock.sendto(response_packet, (client_ip, client_port))
            continue

        # return the origin server's IP if someone is requesting it directly
        if query_packet.question.domain_name == "origin.cdn-test.space":
            response_packet = build_dns_response(query_packet, ORIGIN_IP, 50)

        else:
            try:
                client_coords = get_ip_coords(client_ip, reader)
                closest_server_ip = find_closest_server(client_coords, edge_servers)
            except Exception as e:
                print(f"Error while finding closest server for client {client_ip}: {e}")
                closest_server_ip = edge_servers[0].ip
            response_packet = build_dns_response(query_packet, closest_server_ip, 50)

        sock.sendto(response_packet, (client_ip, client_port))





        




