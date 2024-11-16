from rest_framework.permissions import IsAuthenticated
from User.models import User


class AdminRequiredPermission(IsAuthenticated):
    """
    Custom permission to allow only Admins.
    """
    def has_permission(self, request, view):
            # Ensure the user is authenticated and is an instance of AdminUser
            is_authenticated = super().has_permission(request, view)

            # Try retrieving the AdminUser instance
            try:
                return is_authenticated and request.user.user_type == 'admin'
            except User.DoesNotExist:
                return False



class LawyerRequiredPermission(IsAuthenticated):
    """
    Custom permission to allow only Admins.
    """
    def has_permission(self, request, view):
            # Ensure the user is authenticated and is an instance of AdminUser
            is_authenticated = super().has_permission(request, view)

            # Try retrieving the AdminUser instance
            try:
                return is_authenticated and request.user.user_type == 'lawyer'
            except User.DoesNotExist:
                return False


class UserRequiredPermission(IsAuthenticated):
    """
    Custom permission to allow only Admins.
    """
    def has_permission(self, request, view):
            # Ensure the user is authenticated and is an instance of AdminUser
            is_authenticated = super().has_permission(request, view)

            # Try retrieving the AdminUser instance
            try:
                return is_authenticated and request.user.user_type == 'user'
            except User.DoesNotExist:
                return False



class IsSuperUser(IsAuthenticated):
    """
    Custom permission to allow access only to superuser accounts.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser