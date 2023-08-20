"""Содержит настройки административной панели для приложения users."""
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки отображения модели users в административной панели."""
    list_display = ('username', 'email', 'last_name', 'first_name')
    list_filter = ('username', 'email', 'is_staff', )
