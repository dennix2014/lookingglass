import subprocess
from netmiko import ConnectHandler
import subprocess
import time
import sys

base_dir = '/home/uchechukwu/Documents'
sys.path.insert(1, f'{base_dir}')

from lookingglass.local_settings import cred

initial_html = """<div class="container result">
                <div class="row">
	    	<div class="col-sm">"""

closing_html = """</div></div></div>"""

def conect_to_ipv4_route_server(command):
    server = {
        'device_type': 'linux',
        'host': cred.get('bird_server'),
        'username': cred.get('ssh_user'),
        'password': cred.get('ssh_pass'),
        'port': cred.get('ssh_port_1'),
    }
    net_connect = ConnectHandler(**server)

    out = net_connect.send_command(command, delay_factor=2)
    time.sleep(2)

    output = out.replace('      ', '&emsp;&emsp;').\
        replace('BIRD 1.6.3 ready.\nAccess restricted\n', '').\
        replace('\n', '<br>').replace('\t', '&emsp;&emsp;').\
        replace('   ', '&emsp;&emsp;').\
        replace('    ', '&emsp;&emsp;').\
        replace('     ', '&emsp;&emsp;')

    final_html = initial_html
    final_html += f'<strong>Command: {command}</strong><br><br>'

    final_html += output
    final_html += closing_html
    return final_html



def ping(ip_address):
    
    command = f'ping -c 5 {ip_address}'
    result = conect_to_ipv4_route_server(command)
    return result


def traceroute(ip_address):
    
    command = f'traceroute {ip_address}'
    result = conect_to_ipv4_route_server(command)
    return result


def route(ip_address):

    command = f'please show route for {ip_address}'
    result = conect_to_ipv4_route_server(command)
    return result

def route_detail(ip_address):

    command = f'please show route for {ip_address} all'
    result = conect_to_ipv4_route_server(command)
    return result
