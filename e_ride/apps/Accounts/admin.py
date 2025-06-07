from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Driver, Client

admin.site.register([User, Driver, Client])
# Register your models here.
