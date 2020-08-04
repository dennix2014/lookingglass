from django.shortcuts import render
from django.http import JsonResponse
from .utils import ping, traceroute, route, route_detail
from .forms import CommandForm
from ratelimit.decorators import ratelimit


@ratelimit(key='header:x-cluster-client-ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def home(request):
    if request.method == 'GET':
        form = CommandForm()
        return render(request, 'lg.html', {'form':form})

    elif request.method == 'POST':
        form = CommandForm(request.POST, request.FILES)

        if form.is_valid:
            ip_address = request.POST['ip_address']
            command = request.POST['command']

            form = CommandForm()
            if command == 'ping':
                result = ping(ip_address)
                response = {'result':result }
                return JsonResponse(response) 
            elif command == 'traceroute':
                result = traceroute(ip_address)
                response = {'result':result }
                return JsonResponse(response) 
            elif command == 'route':
                result = route(ip_address)
                response = {'result':result }
                return JsonResponse(response) 
            elif command == 'route detail':
                result = route_detail(ip_address)
                response = {'result':result }
                return JsonResponse(response) 

def beenLimited(request, exception):
    message = '<h3 class="text-danger text-center">A few too many tries for today buddy. Please try again after 5 minutes</h3>'
    response = {'result':message}
    return JsonResponse(response) 
    