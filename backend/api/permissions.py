from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Класс права доступа админу или для чтение.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.staff))
