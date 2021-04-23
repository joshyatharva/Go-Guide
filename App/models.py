from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
import os
import PIL
from GoGuide.settings import BASE_DIR
# validators should be a list
# Create your models here.

def destination_image_upload(instance, filename):
	print("\n\nCALLED\n")
	_, ext = filename.split('.')
	path = os.path.join(BASE_DIR, 'media/Destination')
	if not os.path.exists(path):
		os.makedirs(path)
	filename = f'{BASE_DIR}/media/Destination/{instance.destination_id}.{ext}'
	return filename

def blog_image_upload(instance, filename):
	_, ext = filename.split('.')
	path = os.path.join(BASE_DIR, 'media/Blog')
	if not os.path.exists(path):
		os.makedirs(path)
	filename = f'{BASE_DIR}/media/Blog/{instance.blog_id}.{ext}'
	return filename

def pan_upload(instance, filename):
	_, ext = filename.split('.')
	path = os.path.join(BASE_DIR, f'media/Documents/{instance.document_id}')
	if not os.path.exists(path):
		os.makedirs(path)
	filename = f'{BASE_DIR}/media/Documents/{instance.document_id}/pan.{ext}'
	return filename

def aadhar_upload(instance, filename):
	_, ext = filename.split('.')
	path = os.path.join(BASE_DIR, f'media/Documents/{instance.document_id}')
	if not os.path.exists(path):
		os.makedirs(path)
	filename = f'{BASE_DIR}/media/Documents/{instance.document_id}/aadhar.{ext}'
	return filename

def certificate_upload(instance, filename):
	ext = filename.split('.')[-1]
	path = os.path.join(BASE_DIR, f'media/Documents/{instance.document_id}')
	if not os.path.exists(path):
		os.makedirs(path)
	filename = f'{BASE_DIR}/media/Documents/{instance.document_id}/certificate.{ext}'
	return filename
 

class User(AbstractUser):
	gender_choice = (
		(0, 'on'),
		(1, 'off'),
	)
	user_choice = (
		(True, 'on'),
		(False, 'off'),
	)
	user_id = models.AutoField(primary_key=True)
	user_type = models.BooleanField(choices=user_choice, default=True)
	first_name = models.CharField(max_length=50)
	last_name =  models.CharField(max_length=50)
	username = models.CharField(max_length=50, unique='True')
	gender = models.BooleanField(choices=gender_choice, default=True)
	email = models.EmailField(unique=True)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) 
	profile_pic = models.ImageField(default='default.png')
	password = 	models.CharField(max_length=50)
	account_verified = models.BooleanField(default=False)
	# looks like the below function doesn't work
	def create_superuser(self, username, email, password):
		user = self.create_user(first_name='admin', last_name='admin', username=username, email=email, gender=True, phone_number=123456789, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user

class Tourist(models.Model):
	tourist_id = models.AutoField(primary_key=True)
	user_details = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Documents(models.Model):
	document_id = models.AutoField(primary_key=True)
	pan = models.FileField(upload_to=pan_upload)
	aadhar = models.FileField(upload_to=aadhar_upload)
	certificate = models.FileField(upload_to=certificate_upload)

class Guide(models.Model):
	guide_id = models.AutoField(primary_key=True)
	is_verified = models.BooleanField(default=False)
	user_details = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	guide_documents = models.OneToOneField(Documents, on_delete=models.CASCADE)
	charges = models.PositiveIntegerField(default=1000)

class Blog(models.Model):
	blog_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50)
	content = models.TextField()
	author = models.ForeignKey(Guide, on_delete=models.CASCADE)
	blog_image = models.ImageField(upload_to=blog_image_upload)

class Location(models.Model):
	location_id = models.AutoField(primary_key=True)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	country = models.CharField(max_length=50)
	class Meta:
		unique_together = ('city', 'state', 'country')

class Destination(models.Model):
	destination_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	link_to_location = models.TextField(blank=True)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	destination_image = models.ImageField()
	def save(self, *args, **kwargs):
		UPLOAD_TO = 'Destination/'
		super(Destination, self).save(*args, **kwargs)
		filename = self.destination_image.name
		_, extension = filename.split('.')
		new_name = f"{UPLOAD_TO}{self.destination_id}.{extension}"
		location = r"{BASE_DIR}/media/".format(BASE_DIR=BASE_DIR)
		os.rename(r"{location}/{filename}".format(location=location,filename=filename), r"{location}/{new_name}".format(location=location, new_name=new_name))
		self.destination_image.name = new_name
		print("Path = ", self.destination_image.path)
		print("url = ", self.destination_image.url)
		print("filename = ", self.destination_image.name)
		# super(Book, self).save(*args, **kwargs)
		# super(Destination, self).save(*args, **kwargs)
		# ####
		# filename = self.destination_image.name
		# ext = filename.split('.')[-1]

		# old_path = f'{BASE_DIR}/media/{filename}'
		# new_path = destination_image_upload(self, self.destination_image.name)
		# print(f"OLD PATH: {old_path}\nNEW PATH: {new_path}")
		# os.rename(old_path, new_path)
		# self.destination_image.path = new_path
		# self.destination_image.name = f"media/Destination/{self.destination_id}.{ext}"
		# print(self.destination_image.name)
		# print(f"OLD PATH: {old_path}\nNEW PATH: {new_path}")

		super(Destination, self).save(*args, **kwargs)

class Review(models.Model):
	review_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	reviewer = models.OneToOneField(Tourist, on_delete=models.CASCADE)
	# django doesn't provide OneToManyField so we have to use ForeignKey which is
	# equivalent to Many To One Relationship
	guide_review = models.ForeignKey(Guide, on_delete=models.CASCADE)
	blog_review = models.ForeignKey(Blog, on_delete=models.CASCADE)

class AccountVerification(models.Model):
	av_id = models.AutoField(primary_key=True)
	token = models.CharField(max_length=50)
	user_id = models.IntegerField()
