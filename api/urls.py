from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'programs', views.ProgramViewSet, basename='program')
router.register(r'modules', views.ModuleViewSet, basename='module')
router.register(r'lessons', views.LessonViewSet, basename='lesson')
router.register(r'tests', views.TestViewSet, basename='test')
router.register(r'test-attempts', views.TestAttemptViewSet, basename='test-attempt')
router.register(r'lesson-progress', views.LessonProgressViewSet, basename='lesson-progress')
router.register(r'practice-grades', views.PracticeGradeViewSet, basename='practice-grade')

urlpatterns = [
    path('', include(router.urls)),
]