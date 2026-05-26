
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from training.models import Module


class Test(models.Model):

    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE,
        related_name='test',
        verbose_name='Модуль'
    )
    title = models.CharField(max_length=200, verbose_name='Название теста')
    description = models.TextField(blank=True, verbose_name='Описание')
    time_limit_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name='Лимит времени (минуты)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.title


class Question(models.Model):

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Тест'
    )
    text = models.TextField(verbose_name='Текст вопроса')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self):
        return f"Вопрос {self.order}: {self.text[:50]}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    text = models.CharField(max_length=500, verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f"[{mark}] {self.text[:50]}"


class TestAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_attempts',
        verbose_name='Пользователь'
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Тест'
    )
    attempt_number = models.PositiveIntegerField(
        default=1,
        verbose_name='Номер попытки'
    )
    score = models.FloatField(default=0, verbose_name='Результат (%)')
    total_questions = models.PositiveIntegerField(default=0, verbose_name='Всего вопросов')
    correct_answers = models.PositiveIntegerField(default=0, verbose_name='Правильных ответов')
    is_passed = models.BooleanField(default=False, verbose_name='Сдан')
    is_completed = models.BooleanField(default=False, verbose_name='Завершён')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начало')
    completed_at = models.DateTimeField(
        blank=True, null=True, verbose_name='Завершение'
    )
    locked_until = models.DateTimeField(
        blank=True, null=True, verbose_name='Заблокирован до'
    )

    class Meta:
        verbose_name = 'Попытка теста'
        verbose_name_plural = 'Попытки тестов'
        ordering = ['-started_at']

    def __str__(self):
        status = 'Сдан' if self.is_passed else 'Не сдан'
        return f"{self.user.username} — {self.test.title} (попытка {self.attempt_number}): {status}"

    @property
    def errors_count(self):
        return self.total_questions - self.correct_answers

    @property
    def time_spent(self):
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            total_seconds = int(delta.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        return None


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='Попытка'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Вопрос'
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        verbose_name='Выбранный ответ'
    )
    is_correct = models.BooleanField(default=False, verbose_name='Правильно')

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'
        unique_together = ['attempt', 'question']
