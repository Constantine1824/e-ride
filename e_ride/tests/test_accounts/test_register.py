from django.urls import reverse
import pytest
from rest_framework import fields

@pytest.mark.django_db
class TestRegisterViews:

    def test_client_register(self, auth_token, client, dummy_image):
        from apps.Accounts.serializers import ClientSerializer
        url = reverse('client register')
        profile_img = dummy_image('client.jpeg')
        print(profile_img.file)
        data = {
            "first_name" : 'Ayomide',
            "middle_name" : 'Emman',
            "last_name" : "Taiwo",
            "profile_img" : profile_img.file,
            "gender" : "F"
        }
        # serializer = ClientSerializer(data)
        resp = client.post(url, data, format='multipart')
        print(resp.json())
        assert resp.status_code == 201
        assert resp.json()['data']['user']['role'] == 'client'

    def test_driver_register(self,auth_token, client, dummy_image):
        from apps.Accounts.serializers import DriverCreateSerializer
        url = reverse('driver register')
        profile_img = dummy_image('prof.jpeg')
        license_ = dummy_image('Dereba_license')
        data = {
            "first_name" : "Dereba",
            "middle_name" : 'Oparan',
            "last_name" : "Mutiu",
            "nin" : "1725679747749",
            "profile_img" : profile_img,
            "drivers_license" : license_,
            "gender" : 'Male'
        }
        serialized_data = DriverCreateSerializer(data).data
        resp = client.post(url, serialized_data)
        print(resp.json())
        assert resp.status_code == 201
        assert resp.json()['data']['user']['role'] == 'driver'
