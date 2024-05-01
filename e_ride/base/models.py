from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .managers import UserManager
import uuid
from cloudinary.models import CloudinaryField
from django.contrib.auth.hashers import make_password
from enum import Enum


class GenderChoices(Enum):
    M = 'Male'
    F = 'Female'
    NB = 'Non-Binary'
    PRF = 'Prefer Not To Say'

class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
    

class BaseUser(AbstractBaseUser, BaseModel, PermissionsMixin):
    username = models.CharField(_('username'),max_length=255, unique=True)
    email = models.CharField(_('email'),max_length=32, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        abstract = True

class BaseAccounts(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    middle_name = models.CharField(_('middle name'), max_length=50, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=False, null=False)
    profile_img = CloudinaryField('image')
    gender = models.CharField(max_length=52, choices = [(choice.name, choice.value) for choice in GenderChoices])


    class Meta:
        abstract = True
    
    
    def get_full_name(self):
        return f"{self.first_name} {self.middle_name if self.middle_name else ''} {self.last_name}"
    

    def get_name(self):
        return self.first_name
    

    def get_profile_img(self):
        return self.profile_img.url


    def __str__(self):
        return self.user.username