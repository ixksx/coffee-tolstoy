from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from accounts.models import User
from accounts.serializers import UserSerializer, UserCreateSerializer
from training.models import Program, Module, Lesson, LessonProgress, PracticeGrade
from training.serializers import (
    ProgramSerializer, ModuleSerializer, LessonSerializer,
    LessonProgressSerializer, PracticeGradeSerializer
)
from testing.models import Test, TestAttempt
from testing.serializers import TestSerializer, TestAttemptSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Program.objects.all()
        return Program.objects.filter(role=user.role)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Module.objects.all()
        return Module.objects.filter(program__role=user.role)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Lesson.objects.all()
        return Lesson.objects.filter(module__program__role=user.role)


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


class TestAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestAttemptSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return TestAttempt.objects.all()
        return TestAttempt.objects.filter(user=user)


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return LessonProgress.objects.all()
        return LessonProgress.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PracticeGradeViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeGradeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return PracticeGrade.objects.all()
        return PracticeGrade.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)
