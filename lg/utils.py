import subprocess
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from netmiko import ConnectHandler
import subprocess
import time
import re
from lookingglass.local_settings import commands, servers, server_params


def split_on_empty_lines(s):
    
    # greedily match 2 or more new-lines
    blank_line_regex = r"(?:\r?\n){2,}"
    return re.split(blank_line_regex, s.strip())


ptr_html = """<br><br>
            <div class="container">
                <div class="row">
                <div class="result">
	    	<div class="col-sm"><strong>"""

ptr_close_html = """</strong></div></div></div></div><br><br>"""

bgp_nei_html = """
            <tr>
            <th>Neighbor</th>
            <th>Neighbor Address</th>
            <th>ASN</th>
            <th>BGP State</th>
            <th>Received</th>
            <th>Exported</th>
            </tr>"""

bgp_nei_closing_html = '</table><br><br>'

bgp_nei_rec_html = """
            <tr>
            <th>Prefix</th>
            <th>Origin</th>
            <th>Path</th>
            <th>Local Pref</th>
            </tr>"""

closing_html_3 = '</table><br><br>'


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
    
def connect_to_route_server(server, command):
    start_time = time.time()
    server_params['host'] = servers.get(server)

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

            final_html = ptr_html
            final_html += f'<h4><strong>{command}</strong></h4><br>'

            final_html += out
            final_html += ptr_close_html
            return final_html

        elif command == 'please show protocols all': 

            protocols = split_on_empty_lines(output)

            s = set(protocols)
            for item in s:
                if 'BIRD 1.6.3 ready.' in item or \
                    'BIRD 1.6.0 ready.' in item or \
                    'BIRD 1.4.0 ready.' in item or \
                    'Pipe for ' in item or \
                    'direct1' in item or \
                    'static1' in item or \
                    'kernel1' in item:
                    protocols.remove(item)

            final_html =  f'<table class="all_peers"><caption>{server}: {command}</caption>'
            final_html += bgp_nei_html

            for protocol in protocols:
                final_html += '<tr>'

                description = re.search('Description:    (.*)', protocol)
                if description:
                    final_html += f'<td>{description.group(1)}</td>'
                else:
                    final_html += f'<td>-</td>'

                neighbor_ip = re.search('Neighbor address: (.*)', protocol)
                if neighbor_ip:
                    final_html += f'<td>{neighbor_ip.group(1)}</td>'
                else:
                    final_html += f'<td>-</td>'

                asn = re.search('Neighbor AS:      (\d+)', protocol)
                if asn:
                    final_html += f'<td>{asn.group(1)}</td>'
                else:
                    final_html += f'<td>-</td>'

                bgp_state = re.search('BGP state:          (\w+)', protocol)
                if bgp_state and bgp_state.group(1) == "Established":
                     final_html += f'<td class="green">{bgp_state.group(1)}</td>'
                elif bgp_state:
                    final_html += f'<td class="red">{bgp_state.group(1)}</td>'
    
                received_routes = re.search('Routes:         (\w+)', protocol)
                if received_routes:
                    final_html += f'<td>{received_routes.group(1)}</td>'
                else:
                    final_html += f'<td>-</td>'

                advertised_routes = re.search('imported, (\d+)', protocol)
                if advertised_routes:
                    final_html += f'<td>{advertised_routes.group(1)}</td>'
                else:
                    final_html += f'<td>-</td>'
                final_html += '</tr>'

            final_html += bgp_nei_closing_html
            return final_html

        elif 'please show route protocol' in command:
            final_html =  f'<table class="received"><caption>{server}: {command[:-27]}</caption>'
            final_html += bgp_nei_rec_html

            a = output.splitlines()
            for item in set(a):
                if item == '':
                    a.remove(item)
            
            # Join consecutive lines and treat as one.
            n=2
            output_joined = []
            for i in range(0,len(a),n):
                output_joined.append(a[i] + a[i+1])

            for item in output_joined:

                prefix = item.split(None)[0]
                if prefix:
                    final_html += f'<td>{prefix}</td>'

                origin = re.search(r"\bAS\w+", item)
                if origin:
                    final_html += f'<td>{origin.group()}</td>'
                
                path = re.findall(r"\BGP.as_path:(.*)", item)
                if path:
                    path = ' '.join(path)
                    final_html += f'<td>{path}</td>'
                
                pref = re.search(r'\(\d{1,9}\)', item)
                if pref:
                    final_html += f'<td>{pref.group()[1:-1]}</td>'
                final_html += '</tr>'

            final_html += bgp_nei_closing_html
            return final_html
    else:
        final_html = "<P>Query retured no result</p>"
        return final_html



