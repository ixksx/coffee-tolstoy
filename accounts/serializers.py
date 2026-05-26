
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'role', 'role_display', 'phone',
            'bio', 'avatar', 'date_hired', 'must_change_password',
        ]
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'role', 'password', 'phone', 'date_hired',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.must_change_password = True  # Временный пароль
        user.save()
        return user