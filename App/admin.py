from django.contrib import admin
from .models import User, Tourist, Guide, Blog, Location, Destination, Review, Days, Documents, Booking, AccountVerification

# Register your models here.
admin.site.register(User)
admin.site.register(Tourist)
admin.site.register(Guide)
admin.site.register(Blog)
admin.site.register(Location)
admin.site.register(Destination)
admin.site.register(Review)
admin.site.register(Days)
admin.site.register(Documents)
admin.site.register(Booking)
admin.site.register(AccountVerification)