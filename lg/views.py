import requests
import json
from django.contrib import messages
from django.http import JsonResponse, response
from django.shortcuts import render, redirect, reverse
from django.views.decorators.cache import cache_page
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from ratelimit.decorators import ratelimit
from .forms import CommandForm

from .utils import connect_to_route_server, check_ipv4, check_ipv6, api_get_bgp_peers, api_get_peer_routes, api_get_route_detail, api_update_peers
from lookingglass.local_settings import commands, verification_commands
from lookingglass.servers import servers
from lookingglass.settings import BASE_DIR



def home(request):
    form = CommandForm()
    serverz = [item for item in servers]
    
    context = {
        'form': form,
        'servers': serverz
    }
    if request.method == "GET":
        
        return render(request, 'lg.html', context)
  

def rate_limited(request, exception):
    result = (f'<h3 class="text-danger text-center">'
                f'Too many requests. '
                f'Please try again later</h3>')
    is_table = 0
    response = {
        'result':result, 
        'command': '',
        'is_table': is_table
        }
    return JsonResponse(response) 
    

# @ratelimit(key='header:x-real-ip', 
#             rate='4/m', method=ratelimit.ALL, block=True)

# @ratelimit(key='header:x-real-ip', 
#             rate='20/h', method=ratelimit.ALL, block=True)

# @ratelimit(key='header:x-real-ip', 
#             rate='50/d', method=ratelimit.ALL, block=True)
def ping_trace_route(request):
    if request.method == 'GET' and request.is_ajax():

        ip_address = request.GET['ip_address'].strip()
        command = request.GET['command']
        server = request.GET['server']
        ip_version = (servers.get(server)[0]).split('-')[1].strip()

        if ip_version == 'IPV4':
            check = check_ipv4
        elif ip_version == 'IPV6':
            check = check_ipv6

            
        if check(ip_address):
            check_route = f'{verification_commands.get("check_route")[1]} {ip_address}'
            
            check_route_result = connect_to_route_server(server, check_route)
            if 'Network not in table' in check_route_result[0]:
                output = (f'<p class="error"><strong>"{ip_address}"</strong> '
                            f'not in the routing table</p>')
                is_table = 0

            else:
                command_to_run = f'{commands.get(command)[1]} {ip_address}'
                result = connect_to_route_server(server, command_to_run)
                output = result[0]
                is_table = result[2]

        else:
            output = (f"<p class='error'>{ip_address} is not a valid " 
                        f"{ip_version} address</p>")
            is_table = 0

    response = {
        'result':output, 
        'command': f'{server}: {commands.get(command)[2]} {ip_address}',
        'is_table': is_table
    }
    return JsonResponse(response)



# @ratelimit(key='header:x-real-ip', 
#             rate='4/m', method=ratelimit.ALL, block=True)

# @ratelimit(key='header:x-real-ip', 
#             rate='20/h', method=ratelimit.ALL, block=True)

# @ratelimit(key='header:x-real-ip', 
#             rate='50/d', method=ratelimit.ALL, block=True)
# @cache_page(60 * 15)
def bgp_neighbors(request):
    if request.method == 'GET' and request.is_ajax():
        
        server = request.GET['server']
        command = request.GET['command']

        server = servers.get(server)[1]
        
        result = api_get_bgp_peers(server, command)
        response = {
            'result':result[0], 
            'table_header': result[1],
            'table_id': result[2],
            'is_table': result[4],
            'ip_col': result[5],
            'command': commands.get(command)[2]
            }
        return JsonResponse(response) 
        
    
# @ratelimit(key='header:x-real-ip', 
#             rate='4/m', method=ratelimit.ALL, block=True)

# @ratelimit(key='header:x-real-ip', 
#             rate='20/h', method=ratelimit.ALL, block=True)

# @ratelimit(key='header:x-real-ip', 
#             rate='50/d', method=ratelimit.ALL, block=True)
# @cache_page(60 * 15)
def bgp_neighbor_received(request):
    if request.method == 'GET' and request.is_ajax():

        command = request.GET['command']
        server = request.GET['server']
        protocol = request.GET['protocol']
        peer = request.GET['peer']
        

        server = servers.get(server)[1]

        if "akpamu" in protocol:
            result = 'Route recieved too long'
            is_table = 0
            response = {
                'result':result, 
                'command': f'{commands.get(command)[2]} {protocol}',
                'is_table': is_table
            }
            return JsonResponse(response)
        else:       
            result = api_get_peer_routes(server, command, protocol)
            response = {
                'result':result[0], 
                'table_header': result[1],
                'table_id': result[2],
                'command': f'''{commands.get(command)[2]} from {peer}&emsp;<hr>
                            key: <span class="badge badge-success">P</span> - Primary / active route. 
                            &emsp;<span class="badge badge-warning">N</span> - Inactive route.
                            &emsp;<span><i class="fa-solid fa-triangle-exclamation"></i></span>
                             - Blocked / filtered route''',
                'is_table': result[4],
                'ip_col': result[5],
                'server_ip': server
            }
            return JsonResponse(response)


def route_detail(request):
    if request.method == 'GET' and request.is_ajax():

        server = request.GET['server']
        protocol = request.GET['protocol']
        ip_prefix = request.GET['prefix']
        is_master4 = request.GET['isMaster4']
    
        server = servers.get(server)[1]

        result = api_get_route_detail(server, protocol, ip_prefix, is_master4)
        print(result)
        
        response = {
            'result':result
        }

        return JsonResponse(response)


def update_all(request):

    for server, details in servers.items():
        server_ip = details[1]
        api_update_peers(server, server_ip)
  
    messages.success(request, 'Updated successfully')
    return redirect('home')


def traffics(request, id, heading):
    heading = ' '.join(heading.split('_'))
    graph_ids = {
        0: ['TWO HOURS GRAPH', 'two_hours'],
        1: ['TWO DAYS GRAPH', 'two_days'],
        2: ['THIRTY DAYS GRAPH', 'thirty_days'],
        3: ['ONE YEAR GRAPH', 'one_year']
    }
    base_url = 'https://lg.ixp.net.ng/traffic/&width=900&height=250&graphstyling=baseFontSize%3D%2710%27&'

    context = {
        'graph_ids': graph_ids,
        'id': id,
        'base_url': base_url,
        'heading': heading
    }

    return render(request, 'traffics.html', context)




