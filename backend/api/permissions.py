"""Содержит разрешения, используемые приложением api."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class RecipesPermission(BasePermission):
    """
    Управляет доступом к ресурсу RECIPES. Разрешает использовать:
    - безопасные методы - любому пользователю;
    - POST - авторизованному пользователю;
    - остальные методы - владельцу объекта.
    """

    def has_permission(self, request, view):
        """Возвращает право на доступ к ресурсу в целом."""
        return request.user.is_authenticated or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        """Возвращает право на доступ к конкретному элементу ресурса."""
        return (
            request.method in SAFE_METHODS
            or request.method == "POST"
            or request.user == obj.author
        )
