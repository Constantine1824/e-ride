from django.db import models
from base.models import BaseUser, BaseProfile
from enum import Enum
from cloudinary.models import CloudinaryField

class Roles(Enum):
    DRIVER = "Driver"
    CLIENT = "Client"
    ADMIN = "Admin"
    SUPERADMIN = "Superadmin"


class AvailabityChoices(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ENGAGED = "ENGAGED" #If driver is currently on a ride

class UserRole(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, choices=[(choice.name, choice.value) for choice in Roles])
    permissions = models.ManyToManyField("Permissions")

    def __str__(self):
        return self.name

class User(BaseUser):
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Users'

class Driver(BaseProfile):
    nin = models.BigIntegerField(null=False, blank=False)
    drivers_license = CloudinaryField('image')
    is_verified = models.BooleanField(default=False)
    car_type = models.CharField(max_length=250)
    plate_number = models.CharField(max_length=250)
    availability_status = models.CharField(max_length=25, choices=[(choices.name, choices.value) for choices in AvailabityChoices])
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=120.00)


    def price(self, distance):
        return self.price_per_km * distance

class Client(BaseProfile):
    pass

    
class Permissions(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
# Create your models here.
