from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

# validators should be a list
# Create your models here.

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

	# looks like the below function doesn't work
	def create_superuser(self, username, email, password):
		user = self.create_user(first_name='admin', last_name='admin', username=username, email=email, gender=True, phone_number=123456789, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user

class Tourist(models.Model):
	tourist_id = models.AutoField(primary_key=True)
	user_details = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Guide(models.Model):
	guide_id = models.AutoField(primary_key=True)
	is_verified = models.BooleanField(default=False)
	user_details = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Blog(models.Model):
	blog_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50)
	content = models.TextField()
	author = models.ForeignKey(Guide, on_delete=models.CASCADE)

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
	link_to_location = models.TextField(blank=True)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)


class Review(models.Model):
	review_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	reviewer = models.OneToOneField(Tourist, on_delete=models.CASCADE)
	# django doesn't provide OneToManyField so we have to use ForeignKey which is
	# equivalent to Many To One Relationship
	guide_review = models.ForeignKey(Guide, on_delete=models.CASCADE)
	blog_review = models.ForeignKey(Blog, on_delete=models.CASCADE)
