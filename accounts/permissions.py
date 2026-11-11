from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.permissions import BasePermission

class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'ORGANIZER'
           )

class IsEventOrganizer(BasePermission):
    def has_object_permission(self,request,view,obj):
        return(
            request.user.is_authenticated
            and request.user.role == 'ORGANIZER'
            and obj.organizer == request.user
        )

class IsTicketTypeOrganizer(BasePermission):
    def has_object_permission(self,request,view,obj):
        return(request.user.is_authenticated
               and request.user.role == 'ORGANIZER'
               and obj.event.organizer == request.user)