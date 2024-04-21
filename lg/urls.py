from django.urls import path
from django.views.decorators.cache import cache_page
from lookingglass.local_settings import update_url
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('traffics/<int:id>/<str:heading>/', views.traffics, name='traffics'),
	path('bgp_neighbors/', views.bgp_neighbors, name='bgp_neighbors'),
	path('bgp_neighbor_received/', views.bgp_neighbor_received, name='bgp_neighbor_received'),
	path('route_detail/', views.route_detail, name='route_detail'),
	path(f'{update_url}/', views.update_all, name='update_all'),
]