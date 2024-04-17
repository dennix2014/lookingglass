from django.urls import path
from django.views.decorators.cache import cache_page
from lookingglass.local_settings import update_url
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('ping/', views.ping_trace_route, name='ping'),
	path('traffics/<int:id>/<str:heading>/', views.traffics, name='traffics'),
	path('traceroute/', views.ping_trace_route, name='traceroute'),
	# path('route_detail/', views.ping_trace_route, name='route_detail'),
	path('bgp_neighbors/', views.bgp_neighbors, name='bgp_neighbors'),
	path('bgp_neighbor_received/', views.bgp_neighbor_received, name='bgp_neighbor_received'),
	path('route_detail/', views.route_detail, name='route_detail'),
	path(f'{update_url}/', views.update_all, name='update_all'),
]