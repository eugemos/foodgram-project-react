"""Содержит настройки административной панели для приложения users."""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import User, Subscription


class SubscriptionAdminForm(forms.ModelForm):
    """Форма для отображения модели Subscription в административной панели."""
    def clean(self):
        """Выполняет валидацию формы в целом."""
        data = self.cleaned_data
        if data['user'] == data['subscribed_to']:
            raise ValidationError('Нельзя подписаться на самого себя.')

        return data


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки отображения модели User в административной панели."""
    exclude = ('subscribed_to',)
    list_display = ('username', 'email', 'last_name', 'first_name')
    list_filter = ('username', 'email', 'is_staff', )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки отображения модели Subscription в административной панели."""
    form = SubscriptionAdminForm
    list_display = ('user', 'subscribed_to')
    list_filter = ('user', 'subscribed_to')
