
from rest_framework import serializers
from .models import Test, Question, Answer, TestAttempt, UserAnswer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'answers']


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = '__all__'

    def get_questions_count(self, obj):
        return obj.questions.count()


class TestAttemptSerializer(serializers.ModelSerializer):
    errors_count = serializers.ReadOnlyField()
    time_spent = serializers.ReadOnlyField()

    class Meta:
        model = TestAttempt
        fields = '__all__'
        read_only_fields = ['user']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'