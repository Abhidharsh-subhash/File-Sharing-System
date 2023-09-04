from rest_framework.permissions import BasePermission

class Is_opsuser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
    
class Is_client(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_client
