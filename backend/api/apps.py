"""Содержит настройки приложения api."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Настройки приложения api."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
