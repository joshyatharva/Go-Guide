from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import *
from .forms import CreateUser

# Create your views here.
def index(request):
	return render(request, 'General/home.html')

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
			return HttpResponse("<b>User Created Successfully</b>")
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