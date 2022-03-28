from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели пользователя."""
    class Meta:
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        ]
        model = CustomUser
