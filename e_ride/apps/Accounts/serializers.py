from rest_framework import serializers
from .models import User, Driver, Client, UserRole
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

# driver, creted_ = Role.objects.get_or_create(name='driver')
# client, created = Role.objects.get_or_create(name='client')

class UserCreateSerializer(serializers.ModelSerializer):

    re_password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ["username", "email", \
                  "password", "re_password"]
        extra_kwargs = {
            "password" : {
                "write_only" : True
            }
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise exceptions.ValidationError("password is not the same as re_password")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('re_password')
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    is_active = serializers.BooleanField()
    role = serializers.CharField(allow_null=True)  

class DriverCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Driver
        fields = ["first_name", "middle_name", \
                  "last_name", "profile_img", "nin",\
                  "drivers_license", "is_verified", "user"]
        extra_kwargs = {
            "is_verified" : {
                "read_only" : True
            }
        }

    def create(self, validated_data):
        try: 
            user = self.context['request'].user
            instance = self.Meta.model(**validated_data)
            instance.user = user
            instance.user.role = UserRole.objects.create(name='driver')
            instance.save()
            return instance
        
        except Exception as e:
            raise exceptions.APIException(str(e))

class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Driver
        fields = "__all__"

class ClientCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"

    def create(self, validated_data):
        user = self.context.get('request', {})['user']
        instance = self.Meta.model(**validated_data)
        instance.user = user
        instance.user.role = UserRole.objects.create(name='client')
        instance.save()
        return instance
    
class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def _authenticate(self):
        email = self.validated_data['email']
        password = self.validated_data['password']
        user =User.objects.get(email='ayomidet905@gmail.com')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            update_last_login(None, user)
            return user
        else:
            raise exceptions.AuthenticationFailed('Invalid email or password')
    
    def get_user(self):
        return self._authenticate()

class LoginResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        user_obj = self.context.get('user_obj')
        token = RefreshToken.for_user(user_obj)
        attrs['access'] = str(token.access_token)
        attrs['refresh'] = str(token)
        return super().validate(attrs)