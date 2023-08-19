from django.contrib import admin

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'last_name', 'first_name')
    list_filter = ('username', 'email', 'is_staff', )
