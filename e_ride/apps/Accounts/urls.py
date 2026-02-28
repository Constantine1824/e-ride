from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name="sign up"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('create/driver/', views.DriverRegisterView.as_view(), name="driver register"),
    path('create/client/', views.ClientRegisterView.as_view(), name='client register'),
    path('driver/profile/<uuid:id>', views.DriverProfileView.as_view(), name='driver profile'),
    path('client/profile/<uuid:id>', views.ClientProfileView.as_view(), name='client profile'), 
    path('verify/<token>', views.VerifyMailView.as_view(), name='verify')
]