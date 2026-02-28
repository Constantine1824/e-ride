from django.urls import path
from .views import NearestDriverView, RideRequestsView, RideAcceptView, RideStartView, RideCompleteView, RideCancelView

urlpatterns = [
    path('find_ride', NearestDriverView.as_view(), name='find rides'),
    path('ride_request', RideRequestsView.as_view(), name='ride requests'),
    path('ride/<uuid:ride_id>/accept/', RideAcceptView.as_view(), name='ride-accept'),
    path('ride/<uuid:ride_id>/start/', RideStartView.as_view(), name='ride-start'),
    path('ride/<uuid:ride_id>/complete/', RideCompleteView.as_view(), name='ride-complete'),
    path('ride/<uuid:ride_id>/cancel/', RideCancelView.as_view(), name='ride-cancel'),
]