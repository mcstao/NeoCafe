from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.position == "Админ"
        )


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.position == "Клиент"
        )


class IsBarista(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.position == "Бармен"
        )


class IsWaiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.position == "Официант"
        )


class IsEmailVerified(permissions.BasePermission):
    message = "Вы не подтвердили свою почту"

    def has_permission(self, request, view):
        return request.user.is_verified
