"""Содержит настройки приложения core."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Настройки приложения core."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
