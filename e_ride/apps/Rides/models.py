from django.db import models
from base.models import BaseModel
from apps.Accounts.models import Client, Driver
from base.fields import LocationField

class Ride(BaseModel):
    RIDE_STATUS = (
        ('REQUESTED', 'Ride Requested'),
        ('ACCEPTED', 'Ride Accepted'),
        ('STARTED', 'Ride Started'),
        ('COMPLETED', 'Ride Completed'),
        ('CANCELLED', 'Ride Cancelled'),
    )

    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True) 
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    pickup_location = LocationField()
    dropoff_location = LocationField()
    status = models.CharField(max_length=20, choices=RIDE_STATUS, default='REQUESTED')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    @property
    def ride_distance(self):
        """Calculate the total ride distance in kilometers"""
        if not (self.pickup_location and self.dropoff_location):
            return None
        
        from base.mixins import LocationMixin
        # Create a temporary instance to calculate distance
        temp_instance = LocationMixin()
        temp_instance.location = self.pickup_location
        return temp_instance.distance(self.dropoff_location)
    
    @property
    def driver_to_pickup_distance(self):
        """Calculate distance from driver to pickup location"""
        if not (self.driver.location and self.pickup_location):
            return None
        
        from base.mixins import LocationMixin
        temp_instance = LocationMixin()
        temp_instance.location = self.driver.location
        return temp_instance.distance(self.pickup_location)
    
    @property
    def client_to_driver_distance(self):
        """Calculate current distance between client and driver"""
        if not (self.client.location and self.driver.location):
            return None
        
        from base.mixins import LocationMixin
        temp_instance = LocationMixin()
        temp_instance.location = self.client.location
        return temp_instance.distance_to(self.driver)
    
    @property
    def ride_duration(self):
        """Calculate the total ride duration in seconds"""
        # Placeholder implementation - would need actual duration calculation
        # This could be calculated based on distance and average speed
        if not (self.pickup_location and self.dropoff_location):
            return None
        
        # For now, return None until proper duration calculation is implemented
        # This could use a mapping service API for accurate duration
        return None
    

    def calculate_price(self):
        """Calculate the total price of the ride"""
        if not (self.ride_distance and self.driver.price_per_km):
            return None
       
        self.price= self.ride_distance * self.driver.price_per_km
    
    
# Create your models here.
