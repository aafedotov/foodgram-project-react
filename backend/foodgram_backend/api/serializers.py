from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели пользователя."""
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        return user

    class Meta:
        fields = ['id',
                  'username',
                  'password',
                  'email',
                  'first_name',
                  'last_name',
                  ]

        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True},
                        'first_name': {'required': True},
                        'last_name': {'required': True},
                        'password': {'required': True}
                        }
        model = User


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для эндпоинта смены пароля пользователя."""
    model = User

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)