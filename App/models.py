from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
	user_id = models.AutoField(primary_key=True)
	user_type = models.BooleanField()
	first_name = models.CharField(max_length=50)
	last_name =  models.CharField(max_length=50)
	email = models.EmailField()
	password = 	models.CharField(max_length=50)

class Tourist(models.Model):
	tourist_id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

class Guide(models.Model):
	guide_id = models.AutoField(primary_key=True)
	is_verified = models.BooleanField(default=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE)