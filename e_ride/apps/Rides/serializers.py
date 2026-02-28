from rest_framework import serializers
from apps.Accounts.serializers import DriverSerializer, ClientSerializer
from apps.Accounts.models import Client, Driver
from .models import Ride

class LocationSerializerField(serializers.Field):
    def to_representation(self, value):
        lon, lat = value
        return {
            'lon' : lon,
            'lat' : lat
        }

    def to_internal_value(self, data):
        try:
            if isinstance(data, dict):
                lon = float(data['lon'])
                lat = float(data['lat'])
            else:
                lon, lat = map(float, data)
        except (KeyError, TypeError, ValueError):
            raise serializers.ValidationError("Location must be [lon, lat] or {'lon':..., 'lat': ...}")
        return (lon, lat)

class NearestInstanceSerializer(serializers.Serializer):
    driver = DriverSerializer(source='0')
    distance = serializers.FloatField(source='1')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        driver_data = data.pop('driver')
        return {**driver_data, 'distance':f'{data['distance']} miles'}
    
class RideCreateSerializer(serializers.ModelSerializer):
    pickup_location = LocationSerializerField()
    dropoff_location = LocationSerializerField()

    class Meta:
        model = Ride
        fields = ['id', 'driver', 'pickup_location', 'dropoff_location', 'price', 'status']
        extra_kwargs = {
            'status': {'read_only': True},
            'price': {'read_only': True},
        }
    
    def create(self, validated_data):
        driver_obj = validated_data.pop('driver')
        user = self.context.get('request').user
        client_obj = Client.objects.get(user=user)
        instance = self.Meta.model(**validated_data)
        instance.driver = driver_obj
        instance.client = client_obj
        instance.calculate_price()
        instance.save()
        return instance


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'