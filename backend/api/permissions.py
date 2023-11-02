from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Класс права доступа админу или для чтение.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.staff))


# class IsAuthorOrAdminOrModeratOrReadOnly(permissions.BasePermission):
#     """
#     Класс права доступа админу, модератору, автору или для чтение
#     для Comments, Review.
#     """

#     def has_permission(self, request, view):
#         return (request.method in permissions.SAFE_METHODS
#                 or request.user.is_authenticated)

#     def has_object_permission(self, request, view, obj):
#         return (request.method in permissions.SAFE_METHODS
#                 or request.user.is_superuser
#                 or request.user.is_admin
#                 or request.user.is_moderator
#                 or obj.author == request.user
#                 )
