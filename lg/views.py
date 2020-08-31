from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from ratelimit.decorators import ratelimit
from django.views.decorators.cache import cache_page
#from django.utils.cache import caches
from django.core.cache import cache, caches

from .forms import CommandForm
from .utils import connect_to_route_server, check_ipv4, check_ipv6
from lookingglass.local_settings import servers, server_params, commands



def home(request):
    if request.method == 'GET':
        return render(request, 'lg.html')
    

def beenLimited(request, exception):
    message = '<h3 class="text-danger text-center">A few too many tries for today buddy. Please try again after 5 minutes</h3>'
    response = {'result':message}
    return JsonResponse(response) 
    

@ratelimit(key='header:x-cluster-client-ip', rate='5/m', method=ratelimit.ALL, block=True)
def ping_trace_route(request):
    print(cache.get(request))
    if request.method == 'GET' and request.is_ajax():
        form = CommandForm(request.GET, request.FILES)
        if form.is_valid:
            ip_address = request.GET['ip_address'].strip()
            command = request.GET['command']
            server = request.GET['server']
            
            if command == 'route_detail':
                command_to_run = f'{commands.get(command)} {ip_address} all'
            elif command == 'ping' or command == 'traceroute':
                command_to_run = f'{commands.get(command)} {ip_address}'

            if server != 'rs2.med.v6':
                if check_ipv4(ip_address):
                    result = connect_to_route_server(server, command_to_run)
                    response = {'result':result}
                    return JsonResponse(response) 
                else:
                    result = f'<p class="error"><strong>"{ip_address}"</strong> is not  a valid ipv4 address</p>'
                    response = {'result': result}
                    return JsonResponse(response)
            
            
            elif server == 'rs2.med.v6':
                if check_ipv6(ip_address):
                    result = connect_to_route_server(server, command_to_run)
                    response = {'result':result}
                    return JsonResponse(response) 
                else:
                    result = f'<p class="error"><strong>"{ip_address}"</strong> is not  a valid ipv6 address</p>'
                    response = {'result': result}
                    return JsonResponse(response)


@ratelimit(key='header:x-cluster-client-ip', rate='5/m', method=ratelimit.ALL, block=True)
@cache_page(60 * 15)
def bgp_neighbors(request):
    print(cache.get(request))
    if request.method == 'GET' and request.is_ajax():
        form = CommandForm(request.GET, request.FILES)
        if form.is_valid:
            command = request.GET['command']
            server = request.GET['server']
            
            command_to_run = f'{commands.get(command)}'
            result = connect_to_route_server(server, command_to_run)
            response = {'result':result}
            return JsonResponse(response) 
    

@ratelimit(key='header:x-cluster-client-ip', rate='5/m', method=ratelimit.ALL, block=True)
@cache_page(60 * 15)
def bgp_neighbor_received(request):
    print(cache.get(request))
    if request.method == 'GET' and request.is_ajax():
        form = CommandForm(request.GET, request.FILES)
        if form.is_valid:
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
            




    



        
            
    