from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, который даст доступ на уровне админа"""

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or (
                        request.user.is_authenticated
                        and request.user.is_superuser
                )
        )


class ReadOnly(permissions.BasePermission):
    """Кастомный пермишен, который даст доступ только на чтение"""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, который даст доступ на уровне автора"""

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
                obj.author == request.user
                or request.method in permissions.SAFE_METHODS
        )
