from django.contrib import messages
from django.http import JsonResponse, response
from django.shortcuts import render, redirect, reverse
from django.views.decorators.cache import cache_page
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from ratelimit.decorators import ratelimit
from .forms import CommandForm


from .utils import connect_to_route_server, check_ipv4, check_ipv6
from lookingglass.local_settings import commands
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
    

@ratelimit(key='header:x-real-ip', 
            rate='4/m', method=ratelimit.ALL, block=True)

@ratelimit(key='header:x-real-ip', 
            rate='20/h', method=ratelimit.ALL, block=True)

@ratelimit(key='header:x-real-ip', 
            rate='50/d', method=ratelimit.ALL, block=True)
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
            check_route = f'{commands.get("route_detail")[1]} {ip_address} all'
    
            if 'Network not in table' \
                in connect_to_route_server(server, check_route):
                output = (f'<p class="error"><strong>"{ip_address}"</strong> '
                            f'not in the routing table</p>')
                command = f'{commands.get(command)[1]} {ip_address}'
                is_table = 0

            else:
                command_to_run = f'{commands.get(command)[1]} {ip_address}'
                result = connect_to_route_server(server, command_to_run)
                command = result[1]
                output = result[0]
                is_table = result[2]

        else:
            output = (f"<p class='error'>{ip_address} is not a valid " 
                        f"{ip_version} address</p>")
            command = f'{commands.get(command)[1]} {ip_address}'
            is_table = 0

    response = {
        'result':output, 
        'command': command,
        'is_table': is_table
    }
    return JsonResponse(response)



@ratelimit(key='header:x-real-ip', 
            rate='4/m', method=ratelimit.ALL, block=True)

@ratelimit(key='header:x-real-ip', 
            rate='20/h', method=ratelimit.ALL, block=True)

@ratelimit(key='header:x-real-ip', 
            rate='50/d', method=ratelimit.ALL, block=True)
@cache_page(60 * 15)
def bgp_neighbors(request):
    if request.method == 'GET' and request.is_ajax():
        
        command = request.GET['command']
        server = request.GET['server']
        
        command_to_run = f'{commands.get(command)[1]}'
        result = connect_to_route_server(server, command_to_run)
        response = {
            'result':result[0], 
            'table_header': result[1],
            'table_class': result[2],
            'command': result[3],
            'is_table': result[4]
            }
        return JsonResponse(response) 
        
    
@ratelimit(key='header:x-real-ip', 
            rate='4/m', method=ratelimit.ALL, block=True)

@ratelimit(key='header:x-real-ip', 
            rate='20/h', method=ratelimit.ALL, block=True)

@ratelimit(key='header:x-real-ip', 
            rate='50/d', method=ratelimit.ALL, block=True)
@cache_page(60 * 15)
def bgp_neighbor_received(request):
    if request.method == 'GET' and request.is_ajax():

        command = request.GET['command']
        server = request.GET['server']
        bgp_peer = request.GET['bgp_peer']

        if "HURRICANE" in bgp_peer:
            result = 'Route recieved too long'
            is_table = 0
            response = {
                'result':result, 
                'command': f'{commands.get(command)[1]} {bgp_peer} all',
                'is_table': is_table
            }
            return JsonResponse(response)
        else:       
            command_to_run = (f'{commands.get(command)[1]} {bgp_peer}'
            f' all | egrep "via|BGP.as_path:"')
            result = connect_to_route_server(server, command_to_run)
            response = {
                'result':result[0], 
                'table_header': result[1],
                'table_class': result[2],
                'command': result[3],
                'is_table': result[4]
            }
            return JsonResponse(response)


def update_all(request):
    command = 'please show protocols all'
    for server in servers:
        connect_to_route_server(server, command, True)
  
    messages.success(request, 'Updated successfully')
    return redirect('home')
 
            
    