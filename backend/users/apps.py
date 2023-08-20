"""Содержит настройки приложения users."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Настройки приложения users."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'пользователи+'
