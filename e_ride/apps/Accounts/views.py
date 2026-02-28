from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.signing import SignatureExpired, BadSignature
from .models import User, Driver, Client
from .serializers import (
    UserCreateSerializer, UserSerializer, LoginSerializer,
    LoginResponseSerializer, DriverCreateSerializer, DriverSerializer,
    ClientCreateSerializer, ClientSerializer,
)
from .permissions import IsOwner, IsClient, IsDriver, IsAdmin
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
        client_instance = serializer.save()
        
        # Create response that includes both client profile and user info
        response_data = {
            **serializer.data,
            'user': UserSerializer(client_instance.user).data
        }
        
        return Response({
            "status" : "success",
            "data" : response_data
        },
        status=status.HTTP_201_CREATED
        )
    
class DriverRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DriverCreateSerializer(data=request.data, context={'request' : request})
        serializer.is_valid(raise_exception=True)
        driver_instance = serializer.save()
        
        # Create response that includes both driver profile and user info
        response_data = {
            **serializer.data,
            'user': UserSerializer(driver_instance.user).data
        }
        
        return Response(
            {
                "status" : "success",
                "data" : response_data
            },
            status=status.HTTP_201_CREATED
        )

class DriverProfileView(APIView):
    # Allow any authenticated user to view a driver profile, but later could add more specific permissions
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
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
        except Driver.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "details": "Driver not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
class ClientProfileView(APIView):
    # Only allow users to access their own profile or admins to access any profile
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        try:
            # Check if the requesting user is trying to access their own profile or is an admin
            if str(request.user.id) == str(id) or (request.user.role and request.user.role.name in ['ADMIN', 'SUPERADMIN']):
                queryset = Client.objects.get(id=id)
                serializer = ClientSerializer(queryset)
                return Response(
                    {
                        "status" : "success",
                        "data" : serializer.data
                    },
                    status = status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "status": "failed",
                        "details": "You don't have permission to access this profile"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Client.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "details": "Client not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
class VerifyMailView(APIView):
    def get(self, request, token):
        try:
            username = encoder.url_decode(token)
            user = User.objects.get(username=username)
            if user.is_active:
                return Response(
                    {
                        "status" : "success",
                        "details" : "user already verified"
                    },
                    status=status.HTTP_200_OK
                )
            user.is_active = True
            user.save()
            return Response(
                {
                    "status" : "success",
                    "details" : "user verified"
                },
                status=status.HTTP_200_OK
            )
        except SignatureExpired:
            return Response(
                {
                    "status": "failed",
                    "details" : "Verification token has expired"
                },
                status = status.HTTP_400_BAD_REQUEST
            )
        except BadSignature:
            return Response(
                {
                    "status": "failed",
                    "details" : "Invalid verification token"
                },
                status = status.HTTP_400_BAD_REQUEST
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
