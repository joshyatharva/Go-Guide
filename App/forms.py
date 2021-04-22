from django.forms import ModelForm, Textarea
from django import forms
from .models import User, Tourist, Guide

# Using this form we can easily create users
class CreateUser(ModelForm):
	class Meta:
		model = User
		fields = ['user_type', 'first_name', 'last_name', 'username', 'gender', 'email', 'phone_number', 'password']

class LoginForm(ModelForm):
	class Meta:
		model = User
		fields = ['user_type', 'username', 'password']



#createprofile.html
#fields= [place, price, mon, tue, wed, thu, fri, sat, sun, aadhar_card, pan_card, guide_certificate ]