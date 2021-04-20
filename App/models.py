from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

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
	user_details = models.ForeignKey(User, on_delete=models.CASCADE)

class Guide(models.Model):
	guide_id = models.AutoField(primary_key=True)
	is_verified = models.BooleanField(default=False)
	user_details = models.ForeignKey(User, on_delete=models.CASCADE)