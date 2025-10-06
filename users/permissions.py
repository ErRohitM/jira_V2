from django.db.models import Q
from django.template.context_processors import request
from rest_framework import permissions

from core.models import Tasks
from . models import UserTypeChoices

class UserTypeFlag:
    @staticmethod
    def user_data_isolation(user_type):
        return user_type in [UserTypeChoices.OWNER, UserTypeChoices.MANAGER]


class ManagerPrivileges(permissions.BasePermission):
    """
    Allows access only to authenticated users who are:
    - Superusers, or
    - Managers or User belonging to the same organization as the object
    """
    message = "You must have Organization Admin User Permissions for this."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return UserTypeFlag.user_data_isolation(request.user.user_type)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if UserTypeFlag.user_data_isolation(request.user.user_type):
            # Check if user belongs to the same organization as the object's project
            return request.user.belonging_organization.filter(id=obj.project.organization_id).exists()
        return False

class OwnerPrivileges(permissions.BasePermission):
    """
    Allows access only to authenticated users who are:
    - Superusers, or
    - Owners or Users belonging to the same organization as the object
    """
    message = "You Must have Organization Owner User Permissions for This"
    # authenticated user only
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return UserTypeFlag.user_data_isolation(request.user.user_type)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if UserTypeFlag.user_data_isolation(request.user.user_type):
            # Check if user belongs to the same organization as the object's project
            return request.user.belonging_organization.filter(id=obj.project.organization_id).exists()
        return False

class MemberPrivileges(permissions.BasePermission):
    """
    Allows access only to authenticated users who are:
    - Superusers, OR
    - User assigned to the specific Task object
    """
    message = "You Must have Organization Member Permissions for This"
    # authenticated user only
    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if the user is a assigned member to this task
        if obj.assignees.filter(id=request.user.id).exists():
            return True

        return False


