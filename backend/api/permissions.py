from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Класс права доступа админу или для чтение.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.is_staff or request.user.is_active)))


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Класс права доступа админу, автору, или для чтение.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff
                or obj.author == request.user
                )
