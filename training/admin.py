from django.contrib import admin
from .models import Program, Module, Lesson, LessonFile, LessonImage, LessonProgress, PracticeGrade


class LessonFileInline(admin.TabularInline):
    model = LessonFile
    extra = 1


class LessonImageInline(admin.TabularInline):
    model = LessonImage
    extra = 1


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'created_at']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'order', 'created_at']
    list_filter = ['program']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'number', 'created_at']
    list_filter = ['module__program', 'module']
    inlines = [LessonFileInline, LessonImageInline]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed']


@admin.register(PracticeGrade)
class PracticeGradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'grade', 'graded_at', 'graded_by']
