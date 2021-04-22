from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
import os
import PIL
# validators should be a list
# Create your models here.

def destination_image_upload(instance, filename):
	_, ext = filename.split('.')
	filename = f'Destination/{instance.destination_id}.{ext}'
	return filename

def blog_image_upload(instance, filename):
	_, ext = filename.split('.')
	filename = f'Blog/{instance.blog_id}.{ext}'
	return filename

def pan_upload(instance, filename):
	_, ext = filename.split('.')
	filename = f'Documents/{instance.document_id}/pan/pan.{ext}'
	return filename

def aadhar_upload(instance, filename):
	_, ext = filename.split('.')
	filename = f'Documents/{instance.document_id}/aadhar/aadhar.{ext}'
	return filename

def certificate_upload(instance, filename):
	_, ext = filename.split('.')
	filename = f'Documents/{instance.document_id}/certificate/certificate.{ext}'
	return filename
 

class User(AbstractUser):
	gender_choice = (
		(0, 'Male'),
		(1, 'Female'),
	)
	user_choice = (
		(True, 'Tourist'),
		(False, 'Guide'),
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
	destination_image = models.ImageField(upload_to=destination_image_upload)


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
