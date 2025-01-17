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
import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import paytmchecksum as PaytmChecksum
# from .Paytm import Checksum
from .credentials import MID, MERCHANT_KEY, MY_KEY

WEBSITE = 'http://127.0.0.1:8000'
CHECKSUMVERIFY = None
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

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
		context["destinations"] = False
	return render(request, 'General/homepage.html', context)

def aboutus(request):
	return render(request, 'General/aboutus.html')

def help(request):
	return render(request, 'General/help.html')

@login_required(login_url='login')
def bookings(request):
	user = request.user
	bookings = False
	if user.user_type:
		bookings = user.tourist.booking_set.filter(status=True).all().order_by('-date')
	else:
		bookings = user.guide.booking_set.filter(status=True).all().order_by('-date')
	context = {
		"bookings" : bookings,
	}
	return render(request, 'General/bookings.html', context)

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
	if not user.account_verified:
		return HttpResponseRedirect('not-verified')
	guide = user.guide
	if not guide.is_verified:
		return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		x = request.POST
		image = request.FILES.get('image')
		fb = x.get('fb')
		if fb:
			user.fb = fb
		insta = x.get('insta')
		if insta:
			user.insta = insta
		twitter = x.get('twitter')
		if twitter:
			user.twitter = twitter
		if image:
			user.profile_pic = image
		user.save()
		form0 = DaysForm(x)
		# form1 = DocumentsForm(x, request.FILES)
		charges = x.get("charges")
		city = x.get("city")
		state = x.get("state")
		country = x.get("country")
		bio = x.get("bio")
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
			guide.location = lctn
			guide.save()
			return HttpResponse("<h1>Guide Edit Profile Successful</h1>")
		else:
			return HttpResponse(f"FORM0 : {form0.errors}\n")

	else:
		guide = request.user.guide
		context = {"guide" : guide}
		return render(request, 'General/editprofile.html', context)

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
		messages.info(request, "Please Check Your Email and Verify") 
		# return HttpResponseRedirect(reverse('create-profile'))
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
	else:
		context["destinations"] = False
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
	if not user.account_verified:
		return HttpResponseRedirect('not-verified')
	guide = user.guide
	if guide.is_verified:
		return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		x = request.POST
		form0 = DaysForm(x)
		form1 = DocumentsForm(x, request.FILES)
		image = request.FILES.get('image')
		if image:
			user.image = image
			user.save()
		charges = x.get("charges")
		city = x.get("city")
		state = x.get("state")
		country = x.get("country")
		fb = x.get('fb')
		insta = x.get('insta')
		twitter = x.get('twitter')
		bio = x.get('bio')
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
			guide.fb = fb
			guide.insta = insta
			guide.twitter = twitter
			guide.bio = bio
			guide.days_available = days
			guide.charges = charges
			guide.location = lctn
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
	user = request.user
	if not user.account_verified:
		return HttpResponseRedirect('not-verified')
	user = User.objects.filter(username=username).first()
	if user is None or user.user_type or (not user.guide.is_verified):
		raise Http404("Not Found!")
	guide = user.guide
	reviews = guide.review_set.all()
	allowed = True
	if not request.user.user_type: # guide cannot post review
		allowed = False
	else :
		print("\n\nTourist IT IS\n")
		# rvws = request.user.tourist.review_set
		found = reviews.filter(reviewer=request.user.tourist).all()
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
	today = datetime.date.today()
	lctn = request.POST.get("location")
	guides = Guide.objects.filter(location=lctn, is_verified=True, available=True).all()
	if guides:
		context["guides"] = guides
	else:
		context["guides"] = False
	context["location"] = lctn
	upcoming_dates = []
	upcoming_days = []
	for i in range(0, 7): # 0 to 6
		upcoming_dates.append(next_weekday(today, i))
		upcoming_days.append(upcoming_dates[i].strftime("%A"))
	context["upcoming_dates"] = upcoming_dates
	context["upcoming_days"] = upcoming_days
	return render(request, "General/bookguide.html", context)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_tourist)
def book(request):
	gd_id = request.POST.get('guide_id')
	guide = Guide.objects.filter(pk=gd_id, is_verified=True).first()

	if guide is None:
		raise Http404("<h1>Page Not Found</h1>")
	lctn = guide.location
	bookings = guide.booking_set.filter(status=True).all()
	print(bookings)
	todays_date = datetime.date.today()
	bookings = bookings.filter(date__gte=todays_date).all()
	dates_not_available = []
	
	for booking in bookings:
		dates_not_available.append(booking.date)
	print('NOT available ON = ', dates_not_available)
	days = guide.days_available
	# 0 = Monday, 1=Tuesday, 2=Wednesday...
	available_dates = []
	mon = days.mon
	tue = days.tue
	wed = days.wed
	thu = days.thu
	fri = days.fri
	sat = days.sat
	sun = days.sun
	if mon:
		d = next_weekday(todays_date, 0)
		if d not in dates_not_available:
			available_dates.append(["Monday", d])
	if tue:
		d = next_weekday(todays_date, 1)
		if d not in dates_not_available:
			available_dates.append(["Tuesday", d])
	if wed:
		d = next_weekday(todays_date, 2)
		if d not in dates_not_available:
			available_dates.append(["Wednesday", d])

	if thu:
		d = next_weekday(todays_date, 3)
		if d not in dates_not_available:
			available_dates.append(["Thursday", d])
	if fri:
		d = next_weekday(todays_date, 4)
		if d not in dates_not_available:
			available_dates.append(["Friday", d])
	if sat:
		d = next_weekday(todays_date, 5)
		if d not in dates_not_available:
			available_dates.append(["Saturday", d])
	if sun:
		d = next_weekday(todays_date, 6)
		if d not in dates_not_available:
			available_dates.append(["Sunday", d])
	print("available_dates = ", available_dates)
	if not available_dates:
		available_dates = False

	context = {
		"guide" : guide,
		"location" : lctn,
		"dates" : available_dates,
	}	
	return render(request, 'General/bookconfirm.html', context)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_tourist)
def guide_filter(request):
	user = request.user
	if not user.account_verified:
		return HttpResponseRedirect('not-verified')
	today = datetime.date.today()
	d = today
	lctn = request.POST.get('location')
	gender = request.POST.get('gender')
	days = request.POST.get('days')
	sort = request.POST.get('sort')
	guides = False;
	day1=None;day2=None;day3=None;day4=None;day5=None;day6=None;day7=None;anyday=None;male=None;female=None;unisex=None;p0=None;p1=None;r0=None;r1=None;All=None;
	if gender == "2":
		guides = Guide.objects.filter(location=lctn, is_verified=True).all()
		unisex = "selected"
	elif gender == "1":
		guides = Guide.objects.filter(location=lctn, user_details__gender=True, is_verified=True).all()
		female = "selected"
	elif gender == "0":
		guides = Guide.objects.filter(location=lctn, user_details__gender=False, is_verified=True).all()
		male = "selected"
	else:
		guides = Guide.objects.none()
	if days == "2":
		guides = guides.filter(available=True).all()
		anyday = "selected"

	elif days == "day1":
		day1 = "selected"

	elif days == "day2":
		day2 = "selected"

	elif days == "day3":
		day3 = "selected"

	elif days == "day4":
		day4 = "selected"

	elif days == "day5":
		day5 = "selected"

	elif days == "day6":
		day6 = "selected"

	elif days == "day7":
		day7 = "selected"
	else:
		days = None
		guides = Guide.objects.none() # does not exist
	print("GUIDES INITIALLY => ", guides)
	if (days != "2") and (days is not None): # if not ALL
		day_number = int(days[3])
		which_day_they_meant = (datetime.date.today().weekday() + day_number)%7
		if which_day_they_meant == 0:
			guides = guides.filter(days_available__mon=True).all()
		elif which_day_they_meant == 1:
			guides = guides.filter(days_available__tue=True).all()
		elif which_day_they_meant == 2:
			guides = guides.filter(days_available__wed=True).all()
		elif which_day_they_meant == 3:
			guides = guides.filter(days_available__thu=True).all()
		elif which_day_they_meant == 4:
			guides = guides.filter(days_available__fri=True).all()
		elif which_day_they_meant == 5:
			guides = guides.filter(days_available__sat=True).all()
		elif which_day_they_meant == 6:
			guides = guides.filter(days_available__sun=True).all()

		d = next_weekday(today, which_day_they_meant)
		for guide in guides:
			bookings = guide.booking_set.filter(date__gte=today, status=True).all()
			for b in bookings:
				if b.date == d:
					guides = guides.exclude(guide_id=guide.guide_id)
					break

	print("GUIDES LATER => ", guides)

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

	context = {"All":All,"unisex":unisex,"anyday":anyday,"day1":day1,"day2":day2,"day3":day3,"day4":day4,"day5":day5,"day6":day6,"day7":day7,"p0":p0,"p1":p1,"r0":r0,"r1":r1,"male":male,"female":female}	
	context["guides"] = guides
	context["location"] = lctn
	upcoming_dates = []
	upcoming_days = []
	for i in range(0, 7): # 0 to 6
		upcoming_dates.append(next_weekday(today, i))
		upcoming_days.append(upcoming_dates[i].strftime("%A"))
	context["upcoming_dates"] = upcoming_dates
	context["upcoming_days"] = upcoming_days
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
	guide = Guide.objects.filter(pk=guide_id, is_verified=True).first()
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

@login_required(login_url='login')
@user_passes_test(is_tourist)
def checkout(request):
	user = request.user
	# return HttpResponse("<h1>In Progress</h1>")
	if not user.account_verified:
		return HttpResponseRedirect(reverse('not-verified'))
	if request.method == "POST":
		tourist = request.user.tourist
		gid = request.POST.get('guide_id')
		lid = request.POST.get('location_id')
		guide = Guide.objects.filter(pk=gid).first()
		lctn = Location.objects.filter(pk=lid).first()
		dt = request.POST.get('date') # string of format "April 26, 2021"
		dt = datetime.datetime.strptime(dt, "%B %d, %Y") # datetime object
		dt = dt.date() # date object
		b = Booking(amount=guide.charges, tourist=tourist, guide=guide, location=lctn, date=dt)
		b.save()
		order_id = f"ORDERID_{b.booking_id}"
		amount = guide.charges
		customer_id = tourist.tourist_id
		param_dict = {
			'MID': str(MID),
			'ORDER_ID': str(order_id),
			'TXN_AMOUNT': str(amount),
			'CUST_ID': tourist.user_details.email,
			'INDUSTRY_TYPE_ID':'Retail',
			'WEBSITE':'WEBSTAGING',
			'CHANNEL_ID':'WEB',
			'CALLBACK_URL':'http://localhost:8000/payment',
		}
		global CHECKSUMVERIFY
		param_dict['CHECKSUMHASH'] = PaytmChecksum.generateSignature(param_dict, MERCHANT_KEY)
		CHECKSUMVERIFY = param_dict["CHECKSUMHASH"]
		return render(request, 'General/payment.html', {'param_dict': param_dict, })
	return render(request, 'General/checkout.html')

@csrf_exempt
def payment(request):
	form = request.POST
	
	response_dict = {}
	checksum = None
	print("Printing Keys ....")
	for i in form.keys():
		print(i)
		response_dict[i] = form[i]
		if i == 'CHECKSUMHASH':
			checksum = form[i]
	checksum = response_dict["CHECKSUMHASH"]
	orderid = response_dict["ORDERID"]
	orderid = orderid.split("_")
	booking_id = int(orderid[1])
	print("BOOKING ID = ", booking_id)
	b = Booking.objects.filter(pk=booking_id).first()
	global CHECKSUMVERIFY
	verify = PaytmChecksum.verifySignature(response_dict, MERCHANT_KEY, CHECKSUMVERIFY)
	if verify:
		if response_dict['RESPCODE'] == '01':
			print('order successful')
			
		else:
			print('order was not successful because' + response_dict['RESPMSG'])
		
	if response_dict["STATUS"] == "TXN_SUCCESS":
		b.status = True
	else:
		b.status = False
	b.save()
	# mail customer
	receiver = ''
	subject = ''
	body = ''
	receiver = b.guide.user_details.email
	subject = "New Booking Confirmed"
	body  = f"Hi {b.guide.user_details.first_name} {b.guide.user_details.last_name}!\nYou have been booked as a guide by {b.tourist.user_details.first_name} {b.tourist.user_details.last_name} for {b.date}.\nThanks and Regards,\nTeam Go-Guide\n"
	if b.status:
		for i in range(5): # try mailing 5 times # mails only once # to guide
			if mail(receiver=receiver, subject=subject, body=body):
				break
	
	receiver = b.tourist.user_details.email
	if b.status:
		subject = "Booking Successful"
		body = f"Hi {b.tourist.user_details.first_name} {b.tourist.user_details.last_name}! Your booking has been successful.\n"
		body += f"Booking Details :\nGuide Name : {b.guide.user_details.first_name} {b.guide.user_details.last_name}\n"
		body += f"Amount Paid : {b.guide.charges}\n"
		body += f"City : {b.location.city}\nState : {b.location.state}\nCountry : {b.location.country}\n"
		body += f"Date : {b.date}\n"
		body += f"Contact Details:\n"
		body += f"Phone Number : {b.guide.user_details.phone_number}\nEmail : {b.guide.user_details.email}\n"
		body += "Thanks and Regards,\nTeam Go-Guide"
	else:
		subject = "Booking Not Successful"
		body = f"Your booking on {b.date} was unsuccessful. Please try again later"
		body += f"Thanks and Regards,\nTeam Go-Guide"
	for i in range(5):
		if mail(receiver=receiver, subject=subject, body=body):
			break
	return render(request, 'General/paymentstatus.html', {'response': response_dict})

def forgot_password(request):
		if request.user.is_authenticated:
			return HttpResponseRedirect(reverse('index'))
		if request.method == "POST":
			em = request.POST.get('email_as_input')
			if em:
				email = request.POST.get('email')
				user = User.objects.filter(email=email).first()
				if user is None:
					return HttpResponse("<h1>No Such User</h1>")
				token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
				acnt = AccountVerification()
				acnt.token = token
				acnt.user_id = user.user_id
				acnt.save()
				receiver = email
				subject = "Reset Password"
				body = "copy-paste the link below in your browser to reset your password:\n"
				body += f"{WEBSITE}/reset/password/{user.user_id}/{token}"
				for i in range(5):
					if mail(receiver=receiver, subject=subject, body=body):
						break
				return HttpResponse("Email has been sent to your mailbox.")
			elif request.POST.get('password_as_input'):
				password = request.POST.get('password')
				user_id = request.POST.get('user_id')
				user = User.objects.filter(user_id=user_id).first()
				if user is None:
					return HttpResponse("<h1>No Record Found</h2>")
				user.set_password(password)
				user.save()
				receiver =user. email
				subject = "Password Reset Successful"
				body = "Your password has been reset successfully\n"
				body += f"Thanks and Regards,\nTeam Go-Guide"
				for i in range(5):
					if mail(receiver=receiver, subject=subject, body=body):
						break
				return HttpResponse("<h1>Your Password Has Been Reset Successfully.</h1>")
			else:
				return HttpResponse("<h1>Something Went Wrong!</h1>")
		else:
			context = {
				"email" : True,
			}
		
			return render(request, 'General/forgotpassword.html', context)

@require_GET
def reset_password(request, user_id, token):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))
	user = User.objects.filter(pk=user_id).first()
	accnt = AccountVerification.objects.filter(user_id=user_id).first()
	if accnt.token == token:
		context = {
			"password" : True,
			"user_id" : user.user_id,
		}
		accnt.delete()
		return render(request, 'General/forgotpassword.html', context)
	else:
		raise Http404("<h1>Page Not Found</h1>")
