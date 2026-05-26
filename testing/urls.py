"""URL-маршруты приложения testing."""

from django.urls import path
from . import views

app_name = 'testing'

urlpatterns = [
    path('module/<int:module_id>/', views.test_start_view, name='test_start'),
    path('module/<int:module_id>/take/', views.test_take_view, name='test_take'),
    path('result/<int:attempt_id>/', views.test_result_view, name='test_result'),
]