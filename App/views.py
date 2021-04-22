from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .forms import CreateUser, LoginForm
from .email_settings import mail
import random
import string

WEBSITE = 'http://127.0.0.1:8000'

def is_tourist(user):
	try:
		print("\n\nIS TOURIST CALLED\n\n")
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
	if request.user.is_authenticated:
		if(request.user.user_type):
			return HttpResponseRedirect(reverse('home-tourist'))
		else:
			return HttpResponseRedirect(reverse('home-guide'))
	return render(request, 'General/homepage.html')

def aboutus(request):
	return render(request, 'General/aboutus.html')

def help(request):
	return render(request, 'General/help.html')


def register(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))
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
			token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
			acnt = AccountVerification()
			acnt.token = token
			acnt.user_id = instance.user_id
			acnt.save()
			subject = 'Verify Your Account on Go-Guide'
			body = f'Hi {instance.first_name} {instance.last_name}!\nPlease copy-paste the link below in your browser to verify your account\n{WEBSITE}/acnt/verify/{instance.user_id}/{token}\nThanks and Regards,\nTeam Go-Guide'
			# try sending mail at max 5 times (it will send mail only once)
			for i in range(0,5):
				if(mail(receiver=instance.email, subject=subject, body=body)):
					break
			# something must be wrong with email id
			if (i == 5):
				context = {
					"form" : form,
				}
				return HttpResponseRedirect(request, '<h1>Faulty Email Id! Please Register Again</h1>')
			# everything is fine
			return HttpResponseRedirect(reverse('login')) #HttpResponse("<b>User Created Successfully</b>")
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
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		email = request.POST["email"]
		username = ''
		password = ''
		try :
			usr = User.objects.filter(email=email).first()
			username = usr.username
			password = request.POST["password"]
			user = authenticate(request, username=username, password=password)
		except ObjectDoesNotExist:
			user = None
	
		if user is not None:
			login(request, user)
			if not user.account_verified:
				return render(request, 'General/accountnotverified.html')
			if user.user_type: # True => Tourist
				return HttpResponseRedirect(reverse('home-tourist'))

			else:
				return HttpResponseRedirect(reverse('home-guide'))
		else :
			return HttpResponse(f"<h1>Login Fail, credentials : {email}, {password}</h1>")

	else :
		form = LoginForm()
		context = {
			"form" : form,
		}
		return render(request, 'General/login.html', context)

@login_required(login_url='login')
def log_out(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

@login_required(login_url='login')
@user_passes_test(is_tourist)
def index_tourist(request):
	context = {
		# empty for now
	}
	return render(request, 'General/touristhome.html', context)

@login_required(login_url='login')
@user_passes_test(is_guide)
def index_guide(request):
	context = {
		# empty for now
	}
	return render(request, 'General/guidehome.html', context)


@login_required(login_url='login')
@user_passes_test(is_tourist)
def profile_edit_tourist(request):
	pass


@login_required(login_url='login')
@user_passes_test(is_tourist)
def profile_edit_guide(request):
	if request.method == "POST":
		pass
	else :
		pass

def verify_account(request, a, token):
	acnt = AccountVerification.objects.filter(user_id=a, token=token).first()
	if acnt is None:
		return HttpResponseNotFound('<b>Atharva Set This As Not Found</b>')
	else:
		acnt.delete() # we no longer need it
		user = User.objects.filter(user_id=a).first()
		user.account_verified = True
		user.save() # save changes
		return HttpResponse('</b>Your Account Has Been Verified!<b>')
		
@login_required(login_url='login')
def not_verified(request):
	if (not request.user.is_authenticated) or user.account_verified:
		return HttpResponseRedirect(reverse('index'))
	else:
		return render(request, 'accountnotverified.html')


def add_destination(request):
	if request.method == "POST":
		try : 
			name = request.POST["name"]
			city = request.POST["city"]
			state = request.POST["state"]
			country = request.POST["country"]
			description = request.POST["description"]
			link_to_location = request.POST["link_to_location"]
			image = request.POST["link_to_location"]
			lctn = Location(city=city, state=state, country=country)
			lctn.save()
			dstn = Destination(name=name, description=description, link_to_location=link_to_location, destination_image=image, location=lctn)
			dstn.save()
		except Exception as e:
			return HttpResponse(f"<b>Destination Not Added to The database :: {e}</b>")
		return HttpResponse("<b>Location Added Successfully</b>")
	else:
		return render(request, "General/placeform.html")
	