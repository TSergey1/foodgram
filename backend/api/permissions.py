from rest_framework import permissions


class IsAuthorOrAdminOrModeratOrReadOnly(permissions.BasePermission):
    """
    Класс права доступа админу, автору или для чтение.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or obj.author == request.user
                )
