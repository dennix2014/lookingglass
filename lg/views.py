from django.shortcuts import render
from .utils import ping, traceroute, route, route_detail
from .forms import CommandForm
from ratelimit.decorators import ratelimit


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def home(request):
    if request.method == 'GET':
        form = CommandForm()
        return render(request, 'lg.html', {'form':form})

    elif request.method == 'POST':
        form = CommandForm(request.POST, request.FILES)

        if form.is_valid:
            ip_address = request.POST['ip_address']
            command = request.POST['command']

            if command == 'ping':
                result = ping(ip_address)
                return render(request, 'lg.html', {'form':form, 'result': result})
            elif command == 'traceroute':
                result = traceroute(ip_address)
                return render(request, 'lg.html', {'form':form, 'result': result})
            elif command == 'route':
                result = route(ip_address)
                return render(request, 'lg.html', {'form':form, 'result': result})
            elif command == 'route detail':
                result = route_detail(ip_address)
                return render(request, 'lg.html', {'form':form, 'result': result})

def rate_limited(request, exception):
    rate_limited_message = "Too many probes in a short time buddy. Please try again after 5 minutes."
    return render(request, 'base.html', {'rate_limited_message': rate_limited_message})