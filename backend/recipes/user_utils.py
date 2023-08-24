"""Содержит утилиты для взаимодействия с пользователем."""
from django.contrib.auth import get_user_model

from .models import Recipe


User = get_user_model()


def user_has_in_list(user: User, list_name: str, recipe: Recipe):
    """Возвращает True, если рецепт находится в списке list_name
    пользователя.
    """
    return recipe in getattr(user, list_name).all()

def add_to_list_of_user(user: User, list_name: str, recipe: Recipe):
    """Добавляет рецепт в список list_name пользователя."""
    getattr(user, list_name).add(recipe)

def remove_from_list_of_user(user: User, list_name: str, recipe: Recipe):
    """Удаляет рецепт из списка list_name пользователя."""
    getattr(user, list_name).remove(recipe)
