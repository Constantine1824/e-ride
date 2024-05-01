from django.urls import reverse
import pytest
from django.contrib.auth.backends import BaseBackend

@pytest.mark.django_db
class TestSignUp:
    def test_signup(self, client):
        data = {
            "username" : "aetaiwo",
            "email" : "ayomidet905@gmail.com",
            "password" : "ayomide@taiiiiiwo",
            "re_password" : "ayomide@taiiiiiwo"
        }
        url = reverse('sign up')
        resp = client.post(url, data)
        assert resp.status_code == 201
        assert resp.json()['status'] == "success" 

    def test_signup_fail(self, client):
        url = reverse('sign up')
        data = {
            "username" : "aetaiwo",
            "email" : "ayomidet905@gmail.com",
            "password" : "ayomide@taiiiiiwo",
            "re_password" : "ayomide"
        }
        resp = client.post(url, data)
        print(resp.json())
        assert resp.status_code == 400

    def test_login(self, client, create_user):
        user = create_user(username='aetaiwo', email='ayomidet905@gmail.com', password='Constantine_', is_active=True)
        url = reverse('login')
        data = {
            "email" : "ayomidet905@gmail.com",
            "password" : "Constantine_"
        }
        resp = client.post(url, data)
        print(resp.json())
        assert resp.status_code == 200
        assert 'access' in resp.json()['data']

    def test_login_fail(self, client, create_user):
        user = create_user(username='aetaiwo', email='ayomidet905@gmail.com', password='Tch1244')
        url = reverse('login')
        data = {
            "email" : "ayomidet905@gmail.com",
            "password" : "Tch124"
        }
        resp = client.post(url, data)
        print(resp.json())
        assert resp.status_code == 401
        assert resp.json()['detail'] == 'Invalid email or password'
