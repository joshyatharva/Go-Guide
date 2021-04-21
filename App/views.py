from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *
from .forms import CreateUser, LoginForm


def is_tourist(user):
	try:
		print("is_tourist called")
		return (user.is_authenticated and user.user_type) # user_type == True if user is tourist
	except Exception as e:
		print(f"Exception Occurred :: is_tourist :: {e}")
		return False

def is_guide(user):
	try:
		return user.is_authenticated and (not user.user_type)
	except Exception as e:
		print(f"Exception Occurred :: is_guide :: {e}")
		return False

# Create your views here.
def index(request):
	return render(request, 'General/homepage.html')

def register(request):
	if request.method == "POST":
		# print(request.POST)	
		form = CreateUser(request.POST)
		for key in form:
			print(key, ": ", key.errors)
		# instance = form.save()
		if form.is_valid():
			print("FORM IS VALID")
			
			# Saving details of new user
			# I tried doing form.save() but it wasn't hashing password

			instance = User.objects.create_user(**form.cleaned_data)
			
			print(instance.__dict__)

			# Linking to vendor or customer model
			is_tourist = instance.user_type
			if is_tourist:
				new_tourist = Tourist()
				new_tourist.user_details = instance
				new_tourist.save()
			else:
				new_guide = Guide()
				new_guide.user_details = instance
				new_guide.save()
			return render(request, 'General/Login.html')#HttpResponse("<b>User Created Successfully</b>")
		else:
			# print("Form is invalid")
			context = {
				"form" : form,
			}
			return render(request, 'General/amj_register.html', context)
	else:
		form = CreateUser()
		context = {
			"form" : form,
		}
		return render(request, 'General/amj_register.html', context)

def log_in(request):
	if request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]
		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			if user.user_type: # True => Tourist
				return render(request, 'General/tourihome.html')

			else:
				return render(request, 'General/guidehome.html')

	else :
		form = LoginForm()
		context = {
			"form" : form,
		}
		return render(request, 'General/Login.html', context)

@user_passes_test(is_tourist)
def index_tourist(request):
	context = {
		# empty for now
	}
	return render(request, 'General/touristhome.html', context)

@user_passes_test(is_guide)
def index_guide():
	context = {
		# empty for now
	}
	return render(request, 'General/guidehome.html', context)