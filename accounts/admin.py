"""Регистрация модели пользователя в стандартной админке Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'must_change_password']
    list_filter = ['role', 'must_change_password']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': ('role', 'must_change_password', 'avatar', 'phone', 'bio', 'date_hired')
        }),
    )
