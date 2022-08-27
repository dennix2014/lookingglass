import ast
import json
from operator import indexOf
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



