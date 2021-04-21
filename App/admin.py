from django.contrib import admin
from .models import User, Tourist, Guide, Blog, Location, Destination, Review

# Register your models here.
admin.site.register(User)
admin.site.register(Tourist)
admin.site.register(Guide)
admin.site.register(Blog)
admin.site.register(Location)
admin.site.register(Destination)
admin.site.register(Review)