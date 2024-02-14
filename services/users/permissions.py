from rest_framework import permissions




class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.role == "client"
        )


class IsBarista(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.role == "barista"
        )


class IsWaiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.role == "waiter"
        )


class IsEmailVerified(permissions.BasePermission):
    message = "Вы не подтвердили свою почту"

    def has_permission(self, request, view):
        return request.user.is_verified
