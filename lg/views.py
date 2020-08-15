from django.shortcuts import render
from django.http import JsonResponse
from ipaddress import (ip_network, IPv4Network, 
                        IPv6Network, AddressValueError)
from ratelimit.decorators import ratelimit

from .forms import CommandForm
from .utils import connect_to_route_server
from lookingglass.local_settings import server4, server6, commands


@ratelimit(key='header:x-cluster-client-ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def home(request):
    if request.method == 'GET':
        return render(request, 'lg.html')
    
    elif request.method == 'POST' and request.is_ajax():
        form = CommandForm(request.POST, request.FILES)
        
        if form.is_valid:
            ip_address = request.POST['ip_address'].strip()
            command = request.POST['command']

            try:
                if ip_network(ip_address):
                    if type(ip_network(ip_address)) == IPv4Network:
                        server = server4
                    elif type(ip_network(ip_address)) == IPv6Network:
                        server = server6

                if command == 'route detail':
                    command_to_run = f'{commands.get(command)} {ip_address} all'
                elif command == 'ping' or command == 'traceroute' or command == 'route':
                    command_to_run = f'{commands.get(command)} {ip_address}'
    
                result = connect_to_route_server(server, command_to_run)
                response = {'result':result}
                return JsonResponse(response) 
            except ValueError:
                result = "<p class='error'>Not a valid ipv4 or ipv6 address</p>"
                response = {'result': result}
                return JsonResponse(response)
            


def beenLimited(request, exception):
    message = '<h3 class="text-danger text-center">A few too many tries for today buddy. Please try again after 5 minutes</h3>'
    response = {'result':message}
    return JsonResponse(response) 
    