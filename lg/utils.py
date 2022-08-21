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
 
    start_time = time.time()
    server_params['host'] = (servers.get(server))[1]

    net_connect = ConnectHandler(**server_params)
    output = net_connect.send_command(command, delay_factor=2)
    net_connect.disconnect()
    print("--- %s seconds ---" % (time.time() - start_time))
    if output:

        if 'ping' in command or 'traceroute' in command or \
            'route for' in command:
        
            out = output.replace('      ', '&emsp;&emsp;').\
                replace('BIRD 1.6.3 ready.\nAccess restricted\n', '').\
                replace('BIRD 1.6.8 ready.\nAccess restricted\n', '').\
                replace('BIRD 1.6.0 ready.\nAccess restricted\n', '').\
                replace('BIRD 1.4.0 ready.\nAccess restricted\n', '').\
                replace('\n', '<br>').replace('\t', '&emsp;&emsp;').\
                replace('   ', '&emsp;&emsp;').\
                replace('    ', '&emsp;&emsp;').\
                replace('     ', '&emsp;&emsp;')

            is_table = 0
            
            return [
                out,
                command,
                is_table
            ]
            
        elif not update and command == 'please show protocols all': 

            protocols = split_on_empty_lines(output)

            s = set(protocols)
            for item in s:
                if 'BIRD ' in item or \
                    'Pipe for ' in item or \
                    'direct1' in item or \
                    'device1' in item or \
                    'static1' in item or \
                    'kernel1' in item:
                    protocols.remove(item)

            
            no = 0 #Initialize s/no
            all_protocols = []
            for protocol in protocols:
                pro = {}
                no  += 1
                pro['s/no'] = no

                if servers.get(server)[2] == 'ixpm':
                    description = \
                    re.search('Description:    (.*)', protocol).group(1)
                    description2 = protocol.split()[0]
                    pro['member'] = f'{description} - {description2}'
                    
                else:
                    description = protocol.split()[0]
                    pro['member'] = description

                neighbor_ip = re.search('Neighbor address: (.*)', protocol)
                if neighbor_ip:
                    pro['neighbor_ip'] = f'{neighbor_ip.group(1)}'
                else:
                    pro['neighbor_ip'] = '-'

                asn = re.search('Neighbor AS:      (\d+)', protocol)
                if asn:
                    pro['asn'] = (f'<a href="{he_url}'
                                    f'{asn.group(1)}" target="_blank"'
                                    f' rel="noopener noreferrer">'
                                    f'{asn.group(1)}</a>')
                else:
                    pro['asn'] = '-'

                bgp_state = re.search('BGP state:          (\w+)', protocol)
                if bgp_state and bgp_state.group(1) == "Established":
                     pro['bgp_state'] = \
                     f'<span class="green">{bgp_state.group(1)}</span>'

                elif bgp_state:
                    pro['bgp_state'] = \
                     f'<span class="red">{bgp_state.group(1)}</span>'
                else:
                    pro['bgp_state'] = '-'
    
                received_routes = re.search('Routes:         (\w+)', protocol)

                if received_routes and int(received_routes.group(1)) > 0 \
                    and int(received_routes.group(1)) <= 3000:
                    pro['received'] = \
                        (f'<span class="received-routes"><a href="#">'
                        f'{received_routes.group(1)}</span></td>')
                elif received_routes:
                    pro['received'] = f'{received_routes.group(1)}'
                else:
                    pro['received'] = '-'

                advertised_routes = re.search('imported, (\d+)', protocol)
                if advertised_routes:
                    pro['exported'] = f'{advertised_routes.group(1)}'
                else:
                    pro['exported'] = '-'
                    

                all_protocols.append(pro)
            table_header = [
                's/no',
                'member', 
                'neighbor_ip', 
                'asn', 
                'bgp_state', 
                'received', 
                'exported'
                ]

            table_id = 'all_peers'
            is_table = 1
            ip_col = table_header.index('neighbor_ip')
            return [all_protocols, table_header, table_id, command, is_table, ip_col]

        elif 'please show route protocol' in command:
            
            all_prefixes = []

            a = output.splitlines()
            for item in set(a):
                if item == '':
                    a.remove(item)
            
            # Join consecutive lines and treat as one.
            n=2
            output_joined = []
            for i in range(0,len(a),n):
                output_joined.append(a[i] + a[i+1])

            no = 0 # Initialize s/no
            for item in output_joined:
                prefixes = {}
                no  += 1
                prefixes['s/no'] = no

                prefix = item.split(None)[0]
                if prefix:
                    prefixes['prefix'] = prefix

                origin = re.search(r"\bAS\w+", item)
                if origin:
                    prefixes['origin'] = origin.group()
                
                paths = re.findall(r"\BGP.as_path:(.*)", item)
                if paths:
                    path = [(f'<a href="{he_url}{item.strip()}" '
                            f'target="_blank" rel="noopener noreferrer">'
                            f'{item}</a>') for item in paths[0].lstrip().split()]

                    path = ' '.join(path)
                    prefixes['path'] = path
                
                pref = re.search(r'\(\d{1,9}\)', item)
                if pref:
                    prefixes['local_pref'] = f'{pref.group()[1:-1]}'

                all_prefixes .append(prefixes)
            table_header = [
                's/no',
                'prefix', 
                'origin', 
                'path', 
                'local_pref'
                ]

            table_id = 'received'
            is_table = 1
            ip_col = table_header.index('prefix')

            return [
                all_prefixes, 
                table_header, 
                table_id, 
                command[:-27], 
                is_table,
                ip_col
            ]
            

            

        elif update:
            protocols = split_on_empty_lines(output)

            s = set(protocols)
            for item in s:
                if 'BIRD ' in item or \
                    'Pipe for ' in item or \
                    'direct1' in item or \
                    'device1' in item or \
                    'static1' in item or \
                    'kernel1' in item:
                    protocols.remove(item)

            peers = {}
            if servers.get(server)[2] == 'ixpm': 
                for protocol in protocols:
                    description = \
                        re.search('Description:    (.*)', protocol).group(1)
                    description = description.split(' - ')
                    description2 = protocol.split()[0]
                    peers[description2] = [description[1]]
            else:
                for protocol in protocols:
                    description = protocol.split()[0]
                    peers[description] = [description]

            peers = {k: v for k, v in sorted(peers.items(), key=lambda item: item[1])}
            with open(f'{BASE_DIR}/lg/{server}.json', 'w') as update:
                json.dump(peers, update, indent=1)

    else:
        final_html = "<P>Query retured no result</p>"
        return final_html



