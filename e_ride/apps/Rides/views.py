from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.Accounts.models import Client, Driver
from apps.Accounts.permissions import IsClient, IsDriver
from apps.Rides.serializers import NearestInstanceSerializer, RideCreateSerializer, RideSerializer
from apps.Rides.models import Ride
from django.shortcuts import get_object_or_404
from apps.Rides.permissions import IsRideDriver, IsRideClient, IsRideParticipant

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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        role_name = getattr(user.role, 'name', '').upper() if user.role else ''
        if role_name == 'CLIENT':
            try:
                client_obj = Client.objects.get(user=user)
                active_rides = Ride.objects.filter(
                    client=client_obj, 
                    status__in=['REQUESTED', 'ACCEPTED', 'STARTED']
                )
            except Client.DoesNotExist:
                return Response({'status': 'Failed', 'details': 'Client profile not found'}, status=status.HTTP_404_NOT_FOUND)
        elif role_name == 'DRIVER':
            try:
                driver_obj = Driver.objects.get(user=user)
                active_rides = Ride.objects.filter(
                    driver=driver_obj, 
                    status__in=['REQUESTED', 'ACCEPTED', 'STARTED']
                )
            except Driver.DoesNotExist:
                return Response({'status': 'Failed', 'details': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'status': 'Failed', 'details': 'Only drivers and clients can view active rides'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = RideSerializer(active_rides, many=True)
        return Response({
            'status': 'Success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        role_name = getattr(request.user.role, 'name', '').upper() if request.user.role else ''
        if role_name != 'CLIENT':
            return Response({'status': 'Failed', 'details': 'Only clients can request rides'}, status=status.HTTP_403_FORBIDDEN)
            
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

class RideAcceptView(APIView):
    permission_classes = [IsAuthenticated, IsRideDriver]
    
    def post(self, request, ride_id):
        ride = get_object_or_404(Ride, id=ride_id)
        self.check_object_permissions(request, ride)
        
        if ride.status != 'REQUESTED':
            return Response({'status': 'Failed', 'details': f'Ride cannot be accepted from status {ride.status}'}, status=status.HTTP_400_BAD_REQUEST)
            
        ride.status = 'ACCEPTED'
        ride.save()
        
        driver = ride.driver
        driver.availability_status = 'ENGAGED'
        driver.save()
        
        return Response({'status': 'Success', 'data': RideSerializer(ride).data}, status=status.HTTP_200_OK)

class RideStartView(APIView):
    permission_classes = [IsAuthenticated, IsRideDriver]
    
    def post(self, request, ride_id):
        ride = get_object_or_404(Ride, id=ride_id)
        self.check_object_permissions(request, ride)
        
        if ride.status != 'ACCEPTED':
            return Response({'status': 'Failed', 'details': f'Ride cannot be started from status {ride.status}'}, status=status.HTTP_400_BAD_REQUEST)
            
        ride.status = 'STARTED'
        ride.save()
        
        return Response({'status': 'Success', 'data': RideSerializer(ride).data}, status=status.HTTP_200_OK)

class RideCompleteView(APIView):
    permission_classes = [IsAuthenticated, IsRideDriver]
    
    def post(self, request, ride_id):
        ride = get_object_or_404(Ride, id=ride_id)
        self.check_object_permissions(request, ride)
        
        if ride.status != 'STARTED':
            return Response({'status': 'Failed', 'details': f'Ride cannot be completed from status {ride.status}'}, status=status.HTTP_400_BAD_REQUEST)
            
        ride.status = 'COMPLETED'
        ride.save()
        
        driver = ride.driver
        driver.availability_status = 'ONLINE'
        driver.save()
        
        return Response({'status': 'Success', 'data': RideSerializer(ride).data}, status=status.HTTP_200_OK)

class RideCancelView(APIView):
    permission_classes = [IsAuthenticated, IsRideParticipant]
    
    def post(self, request, ride_id):
        ride = get_object_or_404(Ride, id=ride_id)
        self.check_object_permissions(request, ride)
        
        if ride.status not in ['REQUESTED', 'ACCEPTED']:
            return Response({'status': 'Failed', 'details': f'Ride cannot be cancelled from status {ride.status}'}, status=status.HTTP_400_BAD_REQUEST)
            
        ride.status = 'CANCELLED'
        ride.save()
        
        driver = ride.driver
        if driver and driver.availability_status == 'ENGAGED':
            driver.availability_status = 'ONLINE'
            driver.save()
            
        return Response({'status': 'Success', 'data': RideSerializer(ride).data}, status=status.HTTP_200_OK)
