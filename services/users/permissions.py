from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.position == "admin"
        )


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.position == "client"
        )


class IsBarista(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.position == "barista"
        )


class IsWaiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.position == "waiter"
        )


class IsEmailVerified(permissions.BasePermission):
    message = "Вы не подтвердили свою почту"

    def has_permission(self, request, view):
        return request.user.is_verified
