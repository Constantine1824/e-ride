from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.Accounts.models import Client, Driver
from apps.Rides.serializers import NearestInstanceSerializer, RideCreateSerializer

class NearestDriverView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        client_obj = Client.objects.get(user=request.user)
        lon, lat = request.data['lon', 'lat']
        client_obj.location = (lon, lat) 
        nearest_drivers = client_obj.find_nearest_instances(Driver, limit=7)
        serializer = NearestInstanceSerializer(nearest_drivers, many=True)
        data = {
            'status': 'Success',
            'data' : serializer.data
        }
        return Response(data=data, status=status.HTTP_200_OK)
        
    def get(self, request):
        # Assume User's location is updated
        client_obj = Client.objects.get(user=request.user)
        nearest_drivers = client_obj.find_nearest_instances(Driver, limit=7)
        serializer = NearestInstanceSerializer(nearest_drivers, many=True)
        data = {
            'status' : 'Success',
            'data' : serializer.data
        }
        return Response(data=data, status=status.HTTP_200_OK)

class RideRequestsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Determine the client current location then use that to get closeby drivers
        # Need to figure out a way to get the client current loc maybe using the url params
        pass

    def post(self, request):
        # Receives the payload from the client and creates a ride object with the chosen driver id 
        serializer = RideCreateSerializer(data = request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = {
                'status' : 'Success',
                'data' : serializer.data
            } 
            return Response(data=data, status=status.HTTP_201_CREATED)

# Create your views here.
