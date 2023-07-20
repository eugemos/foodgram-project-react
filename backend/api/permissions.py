from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReceipesPermission(BasePermission):
    """
    Управляет доступом к ресурсу RECEIPES. Разрешает использовать:
    - безопасные методы - любому пользователю;
    - POST - авторизованному пользователю;
    - остальные методы - владельцу объекта.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.method == "POST"
            or request.user == obj.author
        )
