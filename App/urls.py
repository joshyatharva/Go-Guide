from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('home', views.index, name='home'),
	path('register', views.register, name='register'),
	path('login', views.log_in, name='login'),
	path('t/home', views.index_tourist, name='home-tourist'),
	path('g/home', views.index_guide, name='home-guide'),
]