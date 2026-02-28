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
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        # Handle both User model instances and dictionaries
        if hasattr(obj, 'role') and obj.role:
            # If it's a model instance, get the role name
            return getattr(obj.role, 'name', str(obj.role)).lower() if obj.role else None
        elif isinstance(obj, dict) and 'role' in obj:
            # If it's a dictionary with role key
            role_value = obj['role']
            return role_value.lower() if role_value else None
        elif hasattr(obj, '__getitem__') and 'role' in obj:
            # For other dict-like objects
            role_value = obj['role']
            return role_value.lower() if role_value else None
        return None  

class DriverCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Driver
        fields = ["first_name", "middle_name", \
                  "last_name", "nin",\
                   "is_verified", "user"]
        extra_kwargs = {
            "is_verified" : {
                "read_only" : True
            }
        }

    def create(self, validated_data):
        try: 
            request = self.context.get('request')
            user = getattr(request, 'user', None)
            if not user:
                raise exceptions.ValidationError("User not found in request context")
            
            # Get or create the user role for driver
            driver_role, created = UserRole.objects.get_or_create(name='Driver')
            instance = self.Meta.model(**validated_data)
            instance.user = user
            user.role = driver_role
            user.save()  # Save the user with the role first
            instance.save()
            
            # Refresh the user instance to get the updated role
            instance.user.refresh_from_db()
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
        fields = ['user', 'first_name', 'middle_name', 'last_name']

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user:
            raise exceptions.ValidationError("User not found in request context")
        
        # Get or create the user role for client
        client_role, created = UserRole.objects.get_or_create(name='Client')
        instance = self.Meta.model(**validated_data)
        instance.user = user
        user.role = client_role
        user.save()  # Save the user with the role first
        instance.save()
        
        # Refresh the user instance to get the updated role
        instance.user.refresh_from_db()
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