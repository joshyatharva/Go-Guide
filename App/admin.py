from django.contrib import admin
from .models import User, Tourist, Guide

# Register your models here.
admin.site.register(User)
admin.site.register(Tourist)
admin.site.register(Guide)