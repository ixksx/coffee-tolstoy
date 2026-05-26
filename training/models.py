from django.db import models
from django.conf import settings


class Program(models.Model):
   
    ROLE_CHOICES = [
        ('trainee_barista', 'Стажёр-бариста'),
        ('barista', 'Бариста'),
        ('senior_barista', 'Старший бариста'),
        ('cook', 'Повар'),
        ('manager', 'Менеджер'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название программы')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name='Роль'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(
        upload_to='programs/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Номер программы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Программа обучения'
        verbose_name_plural = 'Программы обучения'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class Module(models.Model):
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Программа'
    )
    name = models.CharField(max_length=200, verbose_name='Название модуля')
    description = models.TextField(blank=True, verbose_name='Краткое описание')
    goal = models.TextField(blank=True, verbose_name='Цель модуля')
    image = models.ImageField(
        upload_to='modules/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.program.name} — {self.name}"


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Модуль'
    )
    number = models.PositiveIntegerField(verbose_name='Номер урока')
    title = models.CharField(max_length=200, verbose_name='Название урока')
    image = models.ImageField(
        upload_to='lessons/',
        blank=True,
        null=True,
        verbose_name='Изображение урока'
    )
    content = models.TextField(verbose_name='Материал урока')

    practice_task = models.TextField(
        blank=True,
        verbose_name='Задание на практику'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['number']

    def __str__(self):
        return f"Урок {self.number}: {self.title}"


class LessonFile(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Урок'
    )
    title = models.CharField(max_length=200, verbose_name='Название файла')
    file = models.FileField(upload_to='lesson_files/', verbose_name='Файл')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Файл урока'
        verbose_name_plural = 'Файлы уроков'

    def __str__(self):
        return self.title


class LessonImage(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Урок'
    )
    image = models.ImageField(upload_to='lesson_images/', verbose_name='Изображение')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')

    class Meta:
        verbose_name = 'Изображение урока'
        verbose_name_plural = 'Изображения уроков'


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name='Пользователь'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Урок'
    )
    completed = models.BooleanField(default=False, verbose_name='Завершён')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')

    class Meta:
        verbose_name = 'Прогресс урока'
        verbose_name_plural = 'Прогресс уроков'
        unique_together = ['user', 'lesson']

    def __str__(self):
        status = '✓' if self.completed else '✗'
        return f"{self.user.username} — {self.lesson.title} [{status}]"


class PracticeGrade(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practice_grades',
        verbose_name='Пользователь'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='practice_grades',
        verbose_name='Урок'
    )
    grade = models.PositiveIntegerField(
        verbose_name='Оценка (1-10)',
        help_text='Оценка от 1 до 10'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    graded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='given_grades',
        verbose_name='Оценил'
    )

    class Meta:
        verbose_name = 'Оценка за практику'
        verbose_name_plural = 'Оценки за практику'
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} — {self.lesson.title}: {self.grade}/10"
