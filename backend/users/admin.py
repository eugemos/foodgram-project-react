"""Содержит настройки административной панели для приложения users."""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import User


class UserAdminForm(forms.ModelForm):
    def clean_subscribed_to(self):
        # print(f'\nINSTANCE: {self.instance.pk}\n')
        # print(f'\nC_DATA: {self.cleaned_data}\n')
        value = self.cleaned_data['subscribed_to']
        if value.filter(pk=self.instance.pk).exists():
            raise ValidationError('Нельзя подписаться на самого себя.')
            
        return value


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки отображения модели users в административной панели."""
    form = UserAdminForm
    list_display = ('username', 'email', 'last_name', 'first_name')
    list_filter = ('username', 'email', 'is_staff', )
