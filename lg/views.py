from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.cache import cache_page
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from ratelimit.decorators import ratelimit


from .utils import connect_to_route_server, check_ipv4, check_ipv6
from lookingglass.local_settings import servers, server_params, commands



def home(request):
    if request.method == "GET":
        return render(request, 'lg.html')
  

def beenLimited(request, exception):
    message = (f'<h3 class="text-danger text-center">'
                f'A few too many tries for you today buddy. '
                f'Please try again later</h3>')
    response = {'result':message}
    return JsonResponse(response) 
    

@ratelimit(key='header:x-cluster-client-ip', 
            rate='5/m', method=ratelimit.ALL, block=True)
def ping_trace_route(request):
    if request.method == 'GET' and request.is_ajax():
        
        ip_address = request.GET['ip_address'].strip()
        command = request.GET['command']
        server = request.GET['server']
        
        if command == 'route_detail':
            command_to_run = f'{commands.get(command)} {ip_address} all'
        
        elif command == 'ping' or command == 'traceroute':
            ### Check if ip is in the routing table so as not use the internet
            check_route = f'{commands.get("route")} {ip_address}'
            if 'Network not in table' \
                in connect_to_route_server(server, check_route):
                result = (f'<p class="error"><strong>"{ip_address}"</strong> '
                            f'not in routing table</p>')
                response = {'result': result}
                return JsonResponse(response)
            else:
                command_to_run = f'{commands.get(command)} {ip_address}' 
        
        if server != 'rs2.med.v6':
            if check_ipv4(ip_address):
                result = connect_to_route_server(server, command_to_run)
                response = {'result':result}
                return JsonResponse(response) 
            else:
                result = (f'<p class="error"><strong>"{ip_address}"</strong> '
                            f'is not  a valid ipv4 address</p>')
                response = {'result': result}
                return JsonResponse(response)

        elif server == 'rs2.med.v6':
            if check_ipv6(ip_address):
                result = connect_to_route_server(server, command_to_run)
                response = {'result':result}
                return JsonResponse(response) 
            else:
                result = (f'<p class="error"><strong>"{ip_address}"</strong> '
                            f'is not  a valid ipv6 address</p>')
                response = {'result': result}
                return JsonResponse(response)


@ratelimit(key='header:x-cluster-client-ip', \
            rate='5/m', method=ratelimit.ALL, block=True)
@cache_page(60 * 15)
def bgp_neighbors(request):
    if request.method == 'GET' and request.is_ajax():
        
        command = request.GET['command']
        server = request.GET['server']
        
        command_to_run = f'{commands.get(command)}'
        result = connect_to_route_server(server, command_to_run)
        response = {'result':result}
        return JsonResponse(response) 
    

@ratelimit(key='header:x-cluster-client-ip', \
            rate='5/m', method=ratelimit.ALL, block=True)
@cache_page(60 * 15)
def bgp_neighbor_received(request):
    if request.method == 'GET' and request.is_ajax():
        
        command = request.GET['command']
        abj = request.GET['abj_neighbors']
        los = request.GET['los_neighbors']
        los_v6 = request.GET['los_neighbors_v6']
        server = request.GET['server']
        
        if abj:
            neighbor = abj
        elif los:
            neighbor = los
        elif los_v6:
            neighbor = los_v6
        
        command_to_run = (f'{commands.get(command)} {neighbor}'
        f' all | egrep "via|BGP.as_path:"')
        result = connect_to_route_server(server, command_to_run)
        response = {'result':result}
        return JsonResponse(response)


        
            
    