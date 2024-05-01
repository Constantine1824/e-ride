from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.permissions import IsAuthenticated
from .models import User, Driver, Client
from .serializers import *

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
# Create your views here.
