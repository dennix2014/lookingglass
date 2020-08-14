from django.shortcuts import render
from django.http import JsonResponse
from ratelimit.decorators import ratelimit
import sys

from .forms import CommandForm
from .utils import connect_to_route_server

base_dir = '/home/noc-admin'
sys.path.insert(1, f'{base_dir}')

from lookingglass.local_settings import \
    server4, server6, commands


@ratelimit(key='header:x-cluster-client-ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def home(request):
    if request.method == 'GET':
        return render(request, 'lg.html')
    
    elif request.method == 'POST' and request.is_ajax():
        form = CommandForm(request.POST, request.FILES)
        
        if form.is_valid:
            ip_address = request.POST['ip_address']
            command = request.POST['command']
            protocol = request.POST['protocol']

            if protocol == 'ipv4':
                server = server4
            elif protocol == 'ipv6':
                server = server6

            if command == 'route detail':
                command_to_run = f'{commands.get(command)} {ip_address} all'
            elif command == 'ping' or command == 'traceroute' \
                                        or command == 'route':
                command_to_run = f'{commands.get(command)} {ip_address}'

            result = connect_to_route_server(server, command_to_run)
            response = {'result':result}
            return JsonResponse(response) 


def beenLimited(request, exception):
    message = '''<h3 class="text-danger text-center">
                A few too many tries for today buddy. 
                Please try again after 5 minutes</h3>'''
    response = {'result':message}
    return JsonResponse(response) 
    