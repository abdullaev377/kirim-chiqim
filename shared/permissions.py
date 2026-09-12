from rest_framework.permissions import BasePermission
from accounts.models import DONE, PHOTO_DONE, SELLER, MANAGER, ORDINARY_USER


class IsSellerOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role in [SELLER, MANAGER]


class IsOwnerOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role in [SELLER, MANAGER]

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user == obj.user or request.user.user_role == MANAGER)


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == MANAGER


class IsOrdinaryUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == ORDINARY_USER


class IsVerifiedUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.auth_status in [DONE, PHOTO_DONE]