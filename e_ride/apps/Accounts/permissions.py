from rest_framework import permissions
from .models import UserRole, Roles


class IsDriver(permissions.BasePermission):
    """
    Permission to check if the user is a driver
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Check if user has a driver role
            return (request.user.role and 
                   request.user.role.name == 'DRIVER')
        return False


class IsClient(permissions.BasePermission):
    """
    Permission to check if the user is a client
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Check if user has a client role
            return (request.user.role and 
                   request.user.role.name == 'CLIENT')
        return False


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if the user is an admin
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Check if user has an admin role
            return (request.user.role and 
                   request.user.role.name in ['ADMIN', 'SUPERADMIN'])
        return False


class IsOwner(permissions.BasePermission):
    """
    Permission to check if the user is the owner of the object
    """
    def has_object_permission(self, request, view, obj):
        # Assuming the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # For profile objects that have user relationship
        elif hasattr(obj, 'profile'):
            return obj.profile.user == request.user
        return False


class IsSameUser(permissions.BasePermission):
    """
    Permission to check if the authenticated user is same as the requested user
    """
    def has_permission(self, request, view):
        # This permission is typically used with object-level permissions
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Assuming the obj is a User or has a user attribute
        if hasattr(obj, 'pk'):
            return obj.pk == request.user.pk
        return False