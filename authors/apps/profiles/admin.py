from django.contrib import admin

#local import
from .models import Profile

#we register the profile app on admin 
admin.site.register(Profile)
