from django.urls import path
from .views import NearestDriverView, RideRequestsView

urlpatterns = [
    path('find_ride', NearestDriverView.as_view(), name='find rides'),
    path('ride_request', RideRequestsView.as_view(), name='ride requests')
]