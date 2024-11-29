from rest_framework.permissions import BasePermission

class EmployerPermissions(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.groups.filter(name="employer").exists()
    
class ApplicantPermissions(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.groups.filter(name="applicant").exists()
    