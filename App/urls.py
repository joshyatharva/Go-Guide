from django.urls import path
from . import views

urlpatterns = [

	path('', views.index, name='index'),
	path('aboutus', views.aboutus, name='aboutus'),
	path('help', views.help, name='help'),
	path('home', views.index, name='home'),
	path('register', views.register, name='register'),
	path('login', views.log_in, name='login'),
	path('logout', views.log_out, name='logout'),
	path('t/home', views.index_tourist, name='home-tourist'),
	path('g/home', views.index_guide, name='home-guide'),
	path('t/profile/edit', views.profile_edit_tourist, name='tourist-profile-edit'),
	path('g/profile/edit', views.profile_edit_guide, name='guide-profile-edit'),
	path('acnt/verify/<int:a>/<str:token>', views.verify_account, name='verify-account'),
	path('acnt/not_verified', views.not_verified, name='not-verified'),
]