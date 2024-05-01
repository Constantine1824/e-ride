import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def create_user(django_user_model, db):
    def _create(**kwargs):
        return django_user_model.objects.create_user(**kwargs)
    return _create

@pytest.fixture
def auth_token(django_user_model, client):
    user = django_user_model.objects.create_user(email='ayomidet905@gmail.com', username='aetaiwo', password='ayomide@taiwo')
    user.is_active=True
    user.save()
    url = reverse('login')
    data = {
        'email' : 'ayomidet905@gmail.com',
        'password' : 'ayomide@taiwo'
    }
    resp = client.post(url, data)
    print(resp.json())
    token = resp.json()['data']['access']
    client.credentials(HTTP_AUTHORIZATION = f'Bearer {token}')
    return token

@pytest.fixture
def dummy_image():
    def create_img(img_name):
        content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90?\x0b\xfc\x00\x00\x00\x0dIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xf5\x00\x01\x05\x03\x02\xd5z\x9b\x00\x00\x00\x00IEND\xaeB`\x82'
        return SimpleUploadedFile(img_name, content, content_type='image/jpeg')
    return create_img