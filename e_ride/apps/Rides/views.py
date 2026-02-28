from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.Accounts.models import Client, Driver
from apps.Accounts.permissions import IsClient, IsDriver
from apps.Rides.serializers import NearestInstanceSerializer, RideCreateSerializer, RideSerializer

class NearestDriverView(APIView):
    permission_classes = [IsAuthenticated, IsClient]
    def put(self, request):
        try:
            client_obj = Client.objects.get(user=request.user)
            lon = float(request.data.get('lon'))
            lat = float(request.data.get('lat'))
            client_obj.location = (lon, lat) 
            client_obj.save()
            nearest_drivers = client_obj.find_nearest_instances(Driver, limit=7)
            serializer = NearestInstanceSerializer(nearest_drivers, many=True)
            data = {
                'status': 'Success',
                'data' : serializer.data
            }
            return Response(data=data, status=status.HTTP_200_OK)
        except (TypeError, ValueError):
            return Response(
                {
                    'status': 'Failed',
                    'details': 'Invalid coordinates provided'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def get(self, request):
        # Assume User's location is present
        try:
            client_obj = Client.objects.get(user=request.user)
            nearest_drivers = client_obj.find_nearest_instances(Driver, limit=7)
            serializer = NearestInstanceSerializer(nearest_drivers, many=True)
            data = {
                'status' : 'Success',
                'data' : serializer.data
            }
            return Response(data=data, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {
                    'status': 'Failed',
                    'details': 'Client profile not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

class RideRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsClient]
    def get(self, request):
        try:
            client_obj = Client.objects.get(user=request.user)
            from apps.Rides.models import Ride
            active_rides = Ride.objects.filter(
                client=client_obj, 
                status__in=['REQUESTED', 'ACCEPTED', 'STARTED']
            )
            serializer = RideSerializer(active_rides, many=True)
            return Response({
                'status': 'Success',
                'data': serializer.data,
            },
            status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {
                    'status': 'Failed',
                    'details': 'Client profile not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        try:
            serializer = RideCreateSerializer(data=request.data, context={'request':request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {
                'status' : 'Success',
                'data' : serializer.data
            } 
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {
                    'status': 'Failed',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Create your views here.
