from rest_framework import serializers
from .models import Program, Module, Lesson, LessonFile, LessonImage, LessonProgress, PracticeGrade


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class ModuleCardSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'image', 'lessons_count']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonFile
        fields = '__all__'


class LessonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonImage
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    files = LessonFileSerializer(many=True, read_only=True)
    images = LessonImageSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class LessonCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'number', 'title', 'image']


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = '__all__'
        read_only_fields = ['user']


class PracticeGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeGrade
        fields = '__all__'
        read_only_fields = ['graded_by', 'graded_at']