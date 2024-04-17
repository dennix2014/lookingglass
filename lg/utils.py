import ast
import json
import logging
import requests
import urllib.parse
from operator import indexOf
from pprint import pprint as pp
import subprocess
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from netmiko import ConnectHandler
import subprocess
import time
import re
from lookingglass.local_settings import server_params
from lookingglass.servers import servers
from lookingglass.settings import BASE_DIR
he_url = 'https://bgp.he.net/AS'

lc_definitions ={

(36932, 1101, 1 ): "PREFIX LENGHT TOO LONG",
(36932, 1101, 2 ): "PREFIX_LEN_TOO_SHORT",
(36932, 1101, 3 ): "BOGON",
(36932, 1101, 4 ): "BOGON ASN",
(36932, 1101, 5 ): "AS PATH TOO LONG",
(36932, 1101, 6 ): "AS PATH TOO SHORT",
(36932, 1101, 7 ): "FIRST AS NOT PEER AS",
(36932, 1101, 8 ): "NEXT HOP NOT PEER IP",
(36932, 1101, 9 ): "IRRDB PREFIX FILTERED",
(36932, 1101, 10): "IRRDB ORIGIN AS FILTERED",
(36932, 1101, 11): "PREFIX NOT IN ORIGIN AS",
(36932, 1101, 12): "RPKI UNKNOWN",
(36932, 1101, 13): "RPKI INVALID",
(36932, 1101, 14): "TRANSIT FREE ASN",
(36932, 1101, 15): "TOO MANY COMMUNITIES",
(36932, 1000, 1): "RPKI VALID",
(36932, 1000, 2 ): "RPKI UNKNOWN",
(36932, 1000, 3 ): "RPKI NOT CHECKED",
(36932, 1001, 1 ): "IRRDB VALID",
(36932, 1001, 2 ): "IRRDB NOT CHECKED",
(36932, 1001, 3 ): "IRRDB MORE SPECIFIC",
(36932, 1001, 1000): "IRRDB FILTERED LOOSE",
(36932, 1001, 1001): "IRRDB FILTERED STRICT",
(36932, 1001, 1002): "IRRDB PREFIX EMPTY"
}


def split_on_empty_lines(s):
    
    # greedily match 2 or more new-lines
    blank_line_regex = r"(?:\r?\n){2,}"
    return re.split(blank_line_regex, s.strip())




def check_ipv4(ip_address):

    try:
        if ip_network(ip_address):
            if type(ip_network(ip_address)) == IPv4Network:
                return True
                
    except ValueError:
        return False


def check_ipv6(ip_address):
    
    try:
        if ip_network(ip_address):
            if type(ip_network(ip_address)) == IPv6Network:
                return True 
    except ValueError:
        return False
    
def connect_to_route_server(server, command, update=False):
    server_params['host'] = (servers.get(server))[1]

    net_connect = ConnectHandler(**server_params)
    output = net_connect.send_command(command, delay_factor=2)
    net_connect.disconnect()
    if output:

        if 'ping' in command or 'traceroute' in command or \
            'shroute' in command or 'route for' in command:
            is_table = 0
            
            return [output, command, is_table]
            
        elif command == 'shpro': 
            all_protocols = ast.literal_eval(output)
            table_header = [
                'peer', 'neighbor_ip', 'asn', 
                'bgp_state', 'imported', 'exported'
            ]

            table_id = 'all_peers'
            is_table = 1
            ip_col = table_header.index('neighbor_ip') + 1
            return [all_protocols, table_header, table_id, command, is_table, ip_col]

        elif 'shpref' in command:
            print(output)
            all_prefixes = ast.literal_eval(output)
            table_header = ['prefix', 'origin', 'path']
            table_id = 'received'
            is_table = 1
            ip_col = table_header.index('prefix') + 1

            return [all_prefixes, table_header, table_id, command, is_table, ip_col]
            

        elif update:
            peers = ast.literal_eval(output)
            peers = {k: v for k, v in sorted(peers.items(), key=lambda item: item[1])}
            with open(f'{BASE_DIR}/lg/{server}.json', 'w') as update:
                json.dump(peers, update, indent=1)

    else:
        final_html = "<P>Query retured no result</p>"
        return final_html


def api_get_bgp_peers(server, command):
    endpoint = f"http://{server}/api/protocols/bgp"

    try:
        response = requests.get(endpoint)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()

            # retrieve pertinent peer info from response like neigh, asn, bgp state etc.

            protocols = data.get('protocols')

            all_peer_info = []
            for k,v in protocols.items():
                peer_info = {}

                peer_info['protocol'] = k
                peer_info['peer'] = v.get("description")
                peer_info['neighbor_ip'] = v.get("neighbor_address")
                peer_info['asn'] = v.get("neighbor_as")
                peer_info['bgp_state'] = v.get('bgp_state')
                routes = v.get("routes")
                
                if routes:
                    peer_info['imported'] = routes.get("imported")
                    peer_info['exported'] = routes.get("exported")
                else:
                    peer_info['imported'] = 0
                    peer_info['exported'] = 0

                all_peer_info.append(peer_info)

            table_header = [
                'peer', 'neighbor_ip', 'asn', 
                'bgp_state', 'imported', 'exported', 'protocol'
            ]

            table_id = 'all_peers'
            is_table = 1
            ip_col = table_header.index('neighbor_ip') + 1

            return [all_peer_info, table_header, table_id, command, is_table, ip_col]

        else:
            # If the request was not successful, print the status code
            print("Request was not successful. Status code:", response.status_code)

    except requests.exceptions.RequestException as e:
        # If there was a problem with the request (e.g., network connection issues)
        print("Error making request:", e)


def api_get_peer_routes(server, command, protocol):
    endpoint = f"http://{server}/api/routes/protocol/{protocol}"

    try:
        response = requests.get(endpoint)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()

            # retrieve pertinent peer info from response like neigh, asn, bgp state etc.

            routes = data.get('routes')

            all_routes = []
            for item in routes:
                route = {}
                is_primary = item.get('primary')
                bgp = item.get('bgp')
                large_communities = bgp.get('large_communities')
                prefix = item.get('network')
                is_filtered = False


                for community in large_communities:
                    if community[1] == 1101:
                        is_filtered = True
                        break

                route['prefix'] = prefix
                route['next_hop'] = (item.get('gateway'))
                route['prefix'] = (item.get('network'))
                route['is_filtered'] = is_filtered
                route['is_primary'] = is_primary
                route['detail'] = protocol

                route['path'] = (bgp.get('as_path'))
                route['communities'] = (bgp.get('communities'))
                route['large_communities'] = large_communities

                all_routes.append(route)

            table_header = ['prefix', 'is_primary', 'next_hop', 'path', 'detail']
            table_id = 'received'
            is_table = 1
            ip_col = table_header.index('prefix') + 1

            return [all_routes, table_header, table_id, command, is_table, ip_col]

        else:
            # If the request was not successful, print the status code
            print("Request was not successful. Status code:", response.status_code)

    except requests.exceptions.RequestException as e:
        # If there was a problem with the request (e.g., network connection issues)
        print("Error making request:", e)


def api_get_route_detail(server, protocol, prefix):

    prefix = urllib.parse.quote_plus(prefix)
    endpoint = f"http://{server}/api/route/{prefix}/protocol/{protocol}"
    print(endpoint)

    try:
        response = requests.get(endpoint)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()

            # retrieve pertinent peer info from response like neigh, asn, bgp state etc.

            details = (data.get('routes'))[0]
            route_details = []
            detail = {}

            detail['prefix'] = details.get('network')
            detail['gateway'] = details.get('gateway')
            detail['is_primary'] = details.get('primary')
               
            bgp = details.get('bgp')
            large_communities = bgp.get('large_communities')

            large_communities_defined = []
            for community in large_communities:
                community.append(lc_definitions.get(tuple(community)))
                large_communities_defined.append(community)
                large_communities_defined.append()
            detail['as_path'] = bgp.get('as_path')
            detail['next_hop'] = bgp.get('next_hop')
            detail['large_communities'] = large_communities_defined

            route_details.append(detail)

            return route_details

        else:
            # If the request was not successful, print the status code
            print("Request was not successful. Status code:", response.status_code)

    except requests.exceptions.RequestException as e:
        # If there was a problem with the request (e.g., network connection issues)
        print("Error making request:", e)






