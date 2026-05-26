from django.contrib import admin
from .models import Test, Question, Answer, TestAttempt, UserAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'time_limit_minutes']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'test', 'order']
    list_filter = ['test']
    inlines = [AnswerInline]


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'test', 'attempt_number', 'score',
        'is_passed', 'is_completed', 'started_at'
    ]
    list_filter = ['is_passed', 'is_completed', 'test']


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_answer', 'is_correct']
