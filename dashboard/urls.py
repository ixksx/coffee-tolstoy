"""URL-маршруты кастомной админ-панели."""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Главная панель
    path('', views.dashboard_index, name='index'),
    # Сотрудники
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:user_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:user_id>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:user_id>/delete/', views.employee_delete, name='employee_delete'),
    # Программы
    path('programs/', views.program_list, name='program_list'),
    path('programs/<int:program_id>/edit/', views.program_edit, name='program_edit'),
    # Модули
    path('programs/<int:program_id>/modules/create/', views.module_create, name='module_create'),
    path('modules/<int:module_id>/edit/', views.module_edit, name='module_edit'),
    path('modules/<int:module_id>/delete/', views.module_delete, name='module_delete'),
    # Уроки
    path('modules/<int:module_id>/lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    path('lessons/files/<int:file_id>/delete/', views.lesson_file_delete, name='lesson_file_delete'),
    path('lessons/images/<int:image_id>/delete/', views.lesson_image_delete, name='lesson_image_delete'),
    # Тесты
    path('modules/<int:module_id>/test/', views.test_edit, name='test_edit'),
    path('tests/<int:test_id>/questions/create/', views.question_create, name='question_create'),
    path('questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    # Оценки за практику
    path(
        'employees/<int:user_id>/lessons/<int:lesson_id>/grade/',
        views.practice_grade_view,
        name='practice_grade'
    ),
]