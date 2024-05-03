from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.permissions import IsAuthenticated
from .models import User, Driver, Client
from .serializers import *
from signals.auth_signals import send_mail
from base.utils import UrlSign

encoder = UrlSign()

class SignUpView(APIView):

    def post(self, request):

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status" : "success",
                "data" : serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()
        user_data = UserSerializer(user).data
        payload = {
            "user" : user_data,
        }
        response = LoginResponseSerializer(data=payload, context={"user_obj": user})
        response.is_valid(raise_exception=True)
        return Response(
            {
                "status" : "success",
                "data" : response.data
            }
        )

class RefreshView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "status" : "success",
                "data" : serializer.data
            }
        )

class ClientRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClientCreateSerializer(data=request.data, context={'request' : request})
        serializer.is_valid(raise_exception=True)
        return Response({
            "status" : "success",
            "data" : serializer.data
        },
        status=status.HTTP_201_CREATED
        )
    
class DriverRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DriverCreateSerializer(data=request.data, context={'request' : request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status" : "success",
                "data" : serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class DriverProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        serializer = DriverSerializer
        queryset = Driver.objects.get(id=id)
        serializer = serializer(queryset)
        return Response(
            {
                "status" : "success",
                "data" : serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        queryset = Client.objects.get(id=id)
        serializer = ClientSerializer(queryset)
        return Response(
            {
                "status" : "success",
                "data" : serializer.data
            },
            status = status.HTTP_200_OK
        )
    
class VerifyMailView(APIView):
    def get(self, request, token):
        try:
            username = encoder.url_decode(token)
            user = User.objects.get(username=username)
            user.is_active = True
            return Response(
                {
                    "status" : "success",
                    "details" : "user verified"
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "details" : "User does not exist"
                },
                status = status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "status" : "failed",
                    "details" : str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# Create your views here.
