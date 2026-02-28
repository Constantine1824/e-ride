import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.Accounts.models import Driver, Client, UserRole
from apps.Rides.models import Ride

@pytest.fixture
def driver_client_setup(django_user_model):
    """Setup a driver and a client with roles, profiles and tokens."""
    # Create Roles
    driver_role, _ = UserRole.objects.get_or_create(name='Driver')
    client_role, _ = UserRole.objects.get_or_create(name='Client')

    # Create Driver
    driver_user = django_user_model.objects.create_user(
        username='test_driver', email='driver@test.com', password='password123', is_active=True
    )
    driver_user.role = driver_role
    driver_user.save()
    driver = Driver.objects.create(
        user=driver_user,
        first_name='John',
        last_name='Driver',
        nin=1234567890,
        availability_status='ONLINE',
        price_per_km=150.00,
        location=(6.5244, 3.3792)
    )

    # Create Client
    client_user = django_user_model.objects.create_user(
        username='test_client', email='client@test.com', password='password123', is_active=True
    )
    client_user.role = client_role
    client_user.save()
    client = Client.objects.create(
        user=client_user,
        first_name='Jane',
        last_name='Client',
        location=(6.5244, 3.3792) # Same starting location
    )

    # Setup API Clients with forced authentication
    driver_api = APIClient()
    driver_api.force_authenticate(user=driver_user)
    
    client_api = APIClient()
    client_api.force_authenticate(user=client_user)
    
    return {
        'driver': driver,
        'driver_user': driver_user,
        'driver_api': driver_api,
        'client': client,
        'client_user': client_user,
        'client_api': client_api
    }

@pytest.mark.django_db
class TestRideLifecycle:
    def test_full_ride_lifecycle(self, driver_client_setup):
        setup = driver_client_setup
        client_api = setup['client_api']
        driver_api = setup['driver_api']
        driver = setup['driver']
        
        # 1. Client requests a ride
        request_url = reverse('ride requests')
        request_data = {
            "driver": str(driver.id),
            "pickup_location": [6.5244, 3.3792],
            "dropoff_location": [6.5500, 3.4000] # Some distance away
        }
        resp = client_api.post(request_url, request_data, format='json')
        assert resp.status_code == 201, resp.content
        data = resp.json()['data']
        assert data['status'] == 'REQUESTED'
        assert data['price'] is not None
        assert float(data['price']) > 0
        ride_id = data['id']

        # 2. Driver views active rides
        resp = driver_api.get(request_url)
        assert resp.status_code == 200
        rides = resp.json()['data']
        assert len(rides) == 1
        assert rides[0]['id'] == ride_id

        # 3. Driver accepts ride
        accept_url = reverse('ride-accept', kwargs={'ride_id': ride_id})
        resp = driver_api.post(accept_url)
        assert resp.status_code == 200, resp.content
        assert resp.json()['data']['status'] == 'ACCEPTED'
        
        driver.refresh_from_db()
        assert driver.availability_status == 'ENGAGED'

        # 4. Driver starts ride
        start_url = reverse('ride-start', kwargs={'ride_id': ride_id})
        resp = driver_api.post(start_url)
        assert resp.status_code == 200
        assert resp.json()['data']['status'] == 'STARTED'

        # 5. Driver completes ride
        complete_url = reverse('ride-complete', kwargs={'ride_id': ride_id})
        resp = driver_api.post(complete_url)
        assert resp.status_code == 200
        assert resp.json()['data']['status'] == 'COMPLETED'
        
        driver.refresh_from_db()
        assert driver.availability_status == 'ONLINE'

    def test_client_cancel_ride(self, driver_client_setup):
        setup = driver_client_setup
        client_api = setup['client_api']
        driver_api = setup['driver_api']
        driver = setup['driver']
        
        # Create a ride directly for testing
        request_url = reverse('ride requests')
        request_data = {
            "driver": str(driver.id),
            "pickup_location": [6.5244, 3.3792],
            "dropoff_location": [6.5500, 3.4000]
        }
        resp = client_api.post(request_url, request_data, format='json')
        assert resp.status_code == 201
        ride_id = resp.json()['data']['id']

        # Driver accepts
        accept_url = reverse('ride-accept', kwargs={'ride_id': ride_id})
        driver_api.post(accept_url)
        
        driver.refresh_from_db()
        assert driver.availability_status == 'ENGAGED'

        # Client cancels
        cancel_url = reverse('ride-cancel', kwargs={'ride_id': ride_id})
        resp = client_api.post(cancel_url)
        assert resp.status_code == 200
        assert resp.json()['data']['status'] == 'CANCELLED'

        # Driver should be back to ONLINE
        driver.refresh_from_db()
        assert driver.availability_status == 'ONLINE'
