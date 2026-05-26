"""
Модель пользователя с ролями и флагом принудительной смены пароля.
Роли определяют, какая программа обучения доступна сотруднику.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ('trainee_barista', 'Стажёр-бариста'),
        ('barista', 'Бариста'),
        ('senior_barista', 'Старший бариста'),
        ('cook', 'Повар'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='trainee_barista',
        verbose_name='Роль'
    )
    must_change_password = models.BooleanField(
        default=True,
        verbose_name='Требуется смена пароля'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    date_hired = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата приёма на работу'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def get_role_display_short(self):

        role_map = {
            'trainee_barista': 'Стажёр',
            'barista': 'Бариста',
            'senior_barista': 'Ст. бариста',
            'cook': 'Повар',
            'manager': 'Менеджер',
            'admin': 'Админ',
        }
        return role_map.get(self.role, self.role)
   