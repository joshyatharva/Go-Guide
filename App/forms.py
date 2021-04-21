from django.forms import ModelForm, Textarea
from django import forms
from .models import User, Tourist, Guide

# Using this form we can easily create users
class CreateUser(ModelForm):
	class Meta:
		model = User
		fields = ['user_type', 'first_name', 'last_name', 'username', 'gender', 'email', 'phone_number', 'password', ]

class LoginForm(ModelForm):
	class Meta:
		model = User
		fields = ['user_type', 'username', 'password']