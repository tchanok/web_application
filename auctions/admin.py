from django.contrib import admin
from .models import User, Category, Listing, Comment

# Register your models here.
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Comment)
# admin.site.register(Flight, FlightAdmin)