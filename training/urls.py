
from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    path('about/', views.about_view, name='about'),
    path('modules/', views.modules_view, name='modules'),
    path('modules/<int:module_id>/', views.module_detail_view, name='module_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
    # API endpoints
    path('api/modules/', views.api_modules_list, name='api_modules'),
    path('api/modules/<int:module_id>/lessons/', views.api_lessons_list, name='api_lessons'),
]