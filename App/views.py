from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from .models import *
from .forms import *
from .email_settings import mail
import random
import string
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .Paytm import Checksum
MERCHANT_KEY = '#add here'

WEBSITE = 'http://127.0.0.1:8000'

def is_tourist(user):
	print(type(user.user_type))
	print(user.user_type)
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
	context = {}
	try:
		destinations = Destination.objects.all()[:10]
		context = {
			"destinations" : destinations,
		}
	except Exception as e:
		context = {}
	return render(request, 'General/homepage.html', context)

def aboutus(request):
	return render(request, 'General/aboutus.html')

def help(request):
	return render(request, 'General/help.html')


def register(request):
	if request.user.is_authenticated:
		print(f"\n\nUSERNAME : {request.user.username}\n")
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
			return HttpResponse(f"{form.errors}")
			# print("Form is invalid")
			context = {
				"form" : form,
			}
			return render(request, 'General/registration.html', context)
			# return render(request, 'General/amj_register.html', context)
	else:
		form = CreateUser()
		context = {
			"form" : form,
		}
		return render(request, 'General/registration.html', context)
		# return render(request, 'General/amj_register.html', context)

def log_in(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		email = request.POST.get("email")
		username = ''
		password = ''
		try :
			usr = User.objects.filter(email=email).first()
			username = usr.username
			password = request.POST.get("password")
			user = authenticate(request, username=username, password=password)
		except Exception as e:
			user = None
	
		if user is not None:
			login(request, user)
			if not user.account_verified:
				return HttpResponseRedirect(reverse('not-verified'))
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
	user = request.user
	guide = user.guide
	if not guide.is_verified:
		return HttpResponseRedirect(reverse('create-profile'))
	blogs = guide.blog_set.all()
	context = {
		"blogs" : blogs,
		# empty for now
	}
	return render(request, 'General/guidehome.html', context)


@login_required(login_url='login')
@user_passes_test(is_tourist)
def profile_edit_tourist(request):
	pass


@login_required(login_url='login')
@user_passes_test(is_guide)
def profile_edit_guide(request):
	user = request.user
	guide = user.guide
	if not guide.is_verified:
		return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		x = request.POST
		form0 = DaysForm(x)
		# form1 = DocumentsForm(x, request.FILES)
		charges = x.get("charges")
		city = x.get("city")
		state = x.get("state")
		country = x.get("country")
		lctn = Location.objects.filter(city__icontains=city, state__icontains=state, country__icontains=country).first()
		if not lctn:
			lctn = Location(city=city, state=state, country=country)
			lctn.save()
		if form0.is_valid():
			data = form0.cleaned_data
			mon = data.get('mon')
			tue = data.get('tue')
			wed = data.get('wed')
			thu = data.get('thu')
			fri = data.get('fri')
			sat = data.get('sat')
			sun = data.get('sun')
			days = Days.objects.filter(mon=mon, tue=tue, wed=wed, thu=thu, fri=fri, sat=sat, sun=sun).first()
			if days is None:
				days = form0.save()
			guide.days_available = days
			guide.charges = charges
			guide.location.add(lctn)
			guide.save()
			return HttpResponse("<h1>Guide Edit Profile Successful</h1>")
		else:
			return HttpResponse(f"FORM0 : {form0.errors}\n")

	else:
		return render(request, 'General/editprofile.html')

def verify_account(request, a, token):
	acnt = AccountVerification.objects.filter(user_id=a, token=token).first()
	if acnt is None:
		return HttpResponseNotFound('<b>Page Not Found</b>')
	else:
		acnt.delete() # we no longer need it
		user = User.objects.filter(user_id=a).first()
		user.account_verified = True
		user.save() # save changes
		return HttpResponse('</b>Your Account Has Been Verified!<b>')
		
@login_required(login_url='login')
def not_verified(request):
	user = request.user
	if (not user.is_authenticated) or user.account_verified:
		return HttpResponseRedirect(reverse('index'))
	else:
		if not user.user_type:
			messages.info(request, "Please Check Your Email and Verify") 
			return HttpResponseRedirect(reverse('create-profile'))
		return render(request, 'General/accountnotverified.html')


def add_destination(request):
	if request.method == "POST":
		try : 
			x = request.POST
			form0 = LocationForm(x)
			form1 = DestinationForm(x, request.FILES)
			lctn = ''
			if form0.is_valid():
				lctn = form0.save()
				print("\n\nform0 VALID\n\n")
			else:
				print("\n\nform0 NOT VALID\n\n")

			if form1.is_valid():
				dstn = form1.save(commit=False)
				dstn.location = lctn
				dstn.save()
				print("\n\nform1 VALID\n\n")
			else:
				print(form1.errors)
				print("\n\nform1 NOT VALID\n\n")		

		except Exception as e:
			return HttpResponse(f"<b>Destination Not Added to The database :: {e}</b>")
		return HttpResponse("<b>Location Added Successfully</b>")
	else:
		return render(request, "General/placeform.html")

@require_POST
def search_destination(request):
	destination = request.POST.get("destination")
	destinations = " ".join(destination.split())
	destinations = destinations.split()
	locations = None
	for destination in destinations:
		# qs = Destination.objects.filter(Q(location__city__icontains__trigram_similar=destination)| Q(location__city__icontains__trigram_similar=destination) | Q(location__state__icontains__trigram_similar=destination) | Q(location__country__icontains__trigram_similar=destination))

		qs = Destination.objects.filter(Q(name__icontains=destination)| Q(location__city__icontains=destination) | Q(location__state__icontains=destination) | Q(location__country__icontains=destination))
		if locations is None:
			locations = qs
		else:
			locations.union(qs)
	print(locations)
	context = {}
	if locations is not None:
		context["destinations"] = locations
	for location in locations:
		print(f"\n\nURL : {location.destination_image.url}\n")
		print(f"\n\nURL : {location.destination_image.path}\n")
	# destination search has been done
	return render(request, "General/destination.html", context)
	# return HttpResponse("<b>Rendering for timepass</b>")

@login_required(login_url='login')
@user_passes_test(is_guide)
def create_profile(request):
	user = request.user
	guide = user.guide
	if guide.is_verified:
		return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		x = request.POST
		form0 = DaysForm(x)
		form1 = DocumentsForm(x, request.FILES)
		charges = x.get("charges")
		city = x.get("city")
		state = x.get("state")
		country = x.get("country")
		lctn = Location.objects.filter(city__icontains=city, state__icontains=state, country__icontains=country).first()
		if not lctn:
			lctn = Location(city=city, state=state, country=country)
			lctn.save()
		if form0.is_valid() and form1.is_valid():
			data = form0.cleaned_data
			mon = data.get('mon')
			tue = data.get('tue')
			wed = data.get('wed')
			thu = data.get('thu')
			fri = data.get('fri')
			sat = data.get('sat')
			sun = data.get('sun')
			days = Days.objects.filter(mon=mon, tue=tue, wed=wed, thu=thu, fri=fri, sat=sat, sun=sun).first()
			if days is None:
				days = form0.save()
			documents = form1.save()
			guide.guide_documents = documents
			guide.days_available = days
			guide.charges = charges
			guide.location.add(lctn)
			guide.save()
			return HttpResponse("<h1>Guide Create Profile Successful</h1>")
		else:
			print(f"FORM0 : {form0.errors}")
			print(f"FORM1 : {form1.errors}")
			return HttpResponse(f"FORM0 : {form0.errors}\nFORM1 : {form1.errors}")

	else:
		return render(request, 'General/createprofile.html')



@login_required(login_url='login')
@user_passes_test(is_guide)
def write_blog(request):
	if request.method == "POST":
		x = request.POST
		form = BlogForm(x, request.FILES)
		if form.is_valid():
			blog = form.save(commit=False)
			blog.author = request.user.guide
			blog.save()
			return HttpResponse("<b>Blog Posted Successfully.</b>")
		else:
			messages.warning("Please Write Properly!")
			return render(request, 'General/writeblog.html') 
	else :
		return render(request, 'General/writeblog.html')

@login_required(login_url='login')
def guide_profile(request, username):
	user = User.objects.filter(username=username).first()
	if user is None:
		raise Http404("Not Found!")
	guide = user.guide
	reviews = guide.review_set.all()
	allowed = True
	if not request.user.user_type: # guide cannot post review
		allowed = False
	else :
		print("\n\nTourist IT IS\n")
		rvws = request.user.tourist.review_set
		found = rvws.filter(reviewer=request.user.tourist)
		if found:
			allowed = False
		else:
			allowed = True
	context = {
		"guide" : guide,
		"reviews" : reviews,
		"allowed" : allowed,
	}
	print(f"\n\n{guide.user_details.profile_pic.path}\n{guide.user_details.profile_pic.url}")
	return render(request, "General/profile.html", context)

def read_blogs(request):
	blogs = Blog.objects.all()
	context = {
		"blogs" : blogs,
	}
	return render(request, 'General/blogs.html', context)

@login_required(login_url='login')
@user_passes_test(is_tourist)
@require_POST
def book_guide(request):
	context = {}
	lctn = request.POST.get("location")
	guides = Guide.objects.filter(location=lctn).all()
	if guides:
		context["guides"] = guides
	else:
		context["guides"] = False
	context["location"] = lctn
	return render(request, "General/bookguide.html", context)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_tourist)
def book(request):
	gd_id = request.POST.get('guide_id')
	guide = Guide.objects.filter(pk=gd_id).first()
	if guide is None:
		raise Http404("<h1>Page Not Found</h1>")
	else:
		return HttpResponse("<h1>Yet To Be Processed</h1>")

@require_POST
@login_required(login_url='login')
@user_passes_test(is_tourist)
def guide_filter(request):
	lctn = request.POST.get('location')
	gender = request.POST.get('gender')
	days = request.POST.get('days')
	sort = request.POST.get('sort')
	guides = False;
	mon=None;tue=None;wed=None;thu=None;fri=None;sat=None;sun=None;anyday=None;male=None;female=None;unisex=None;p0=None;p1=None;r0=None;r1=None;All=None;
	if gender == "2":
		guides = Guide.objects.filter(location=lctn).all()
		unisex = "selected"
	elif gender == "1":
		guides = Guide.objects.filter(location=lctn, user_details__gender=True).all()
		female = "selected"
	elif gender == "0":
		guides = Guide.objects.filter(location=lctn, user_details__gender=False).all()
		male = "selected"
	else:
		guides = Guide.objects.none()
	if days == "2":
		guides = guides.filter(available=True).all()
		anyday = "selected"
	elif days == "mon":
		guides = guides.filter(days_available__mon=True).all()
		mon = "selected"
	elif days == "tue":
		guides = guides.filter(days_available__tue=True).all()
		tue = "selected"
	elif days == "wed":
		guides = guides.filter(days_available__wed=True).all()
		wed = "selected"
	elif days == "thu":
		guides = guides.filter(days_available__thu=True).all()
		thu = "selected"
	elif days == "fri":
		guides = guides.filter(days_available__fri=True).all()
		fri = "selected"
	elif days == "sat":
		guides = guides.filter(days_available__sat=True).all()
		sat = "selected"
	elif days == "sun":
		guides = guides.filter(days_available__sun=True).all()
		sun = "selected"
	else:
		guides = Guide.objects.none() # does not exist
	if sort == "2":
		All = "selected"
		pass
	elif sort == "p0":
		guides = guides.order_by('charges')
		p0 = "selected"
	elif sort == "p1":
		guides = guides.order_by('-charges')
		p1 = "selected"
	elif sort == "r0":
		guides = guides.order_by('rating')
		r0 = "selected"
	elif sort == "r1":
		guides = guides.order_by('-rating')
		r1 = "selected"
	else :
		guides = Guide.objects.none()
	context = {"All":All,"unisex":unisex,"anyday":anyday,"mon":mon,"tue":tue,"wed":wed,"thu":thu,"fri":fri,"sat":sat,"sun":sun,"p0":p0,"p1":p1,"r0":r0,"r1":r1,"male":male,"female":female}	
	context["guides"] = guides
	context["location"] = lctn
	return render(request, 'General/bookguide.html', context)
	pass

@require_POST
@login_required(login_url='login')
@user_passes_test(is_tourist)
def review_guide(request):
	# title = request.POST.get('title')
	description = request.POST.get('description')
	rating = int(request.POST.get('rating'))
	guide_id = request.POST.get('guide_id')
	print(description, " ", rating, " ", guide_id)
	guide = Guide.objects.filter(pk=guide_id).first()
	if guide is None:
		raise Http404("<h1>Page Not found</h1>")
	review = Review(description=description, rating=rating, guide_review=guide, reviewer=request.user.tourist)
	review.save()
	query_set = guide.review_set.all()
	n = query_set.count() # this includes the current review
	print("\n\nN = ", n)
	guide.rating = (guide.rating * (n-1) + rating)/n;
	guide.save()

	return redirect('guide-profile', username=guide.user_details.username)
	pass
# def checkout(request):
# 	if request.method == "POST":
# 		x = request.POST
#
# 	 	param_dict = {
#              'MID':'',   #Merchant Id here
#              'ORDER_ID':'',     #order ID here
#              'TXN_AMOUNT':'1',        #payment amount here
#              'CUST_ID':'',			  #customer id or email id here
#              'INDUSTRY_TYPE_ID':'Retail',
#              'WEBSITE':'WEBSTAGING',
#              'CHANNEL_ID':'WEB',
#   	         'CALLBACK_URL':'http://localhost:8000/payment/',
#  		}
# 		param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
# 		return render(request, 'General/payment.html', {'param_dict': param_dict})
#
# 	return render(request, 'General/checkout.html')
#
# @csrf_exempt
# def payment(request):
# 	form = request.POST
# 	response_dict = {}
# 	for i in form.keys():
# 		response_dict[i] = form[i]
# 		if i == 'CHECKSUMHASH':
# 			checksum = form[i]
#
# 	verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
# 	if verify:
# 		if response_dict['RESPCODE'] == '01':
# 			print('order successful')
# 		else:
# 			print('order was not successful because' + response_dict['RESPMSG'])
# 	return render(request, 'General/Paymentstatus.html', {'response': response_dict})
