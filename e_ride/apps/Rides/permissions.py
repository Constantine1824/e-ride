from rest_framework import permissions

class IsRideDriver(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'driver') and obj.driver and obj.driver.user == request.user

class IsRideClient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'client') and obj.client and obj.client.user == request.user

class IsRideParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_driver = hasattr(obj, 'driver') and obj.driver and obj.driver.user == request.user
        is_client = hasattr(obj, 'client') and obj.client and obj.client.user == request.user
        return is_driver or is_client
