from rest_framework import serializers

from django.contrib.auth import get_user_model
from app.models import (
    Tag, Ingredient, MeasurementUnit, IngredientUnit, RecipeIngredient, Recipe
)

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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        fields = ('__all__')
        model = Tag


class MeasurementUnitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        fields = ('name',)
        model = MeasurementUnit


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    name = serializers.CharField()

    class Meta:
        fields = ('name',)
        model = Ingredient


class IngredientUnitSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов и единиц измерения."""

    name = serializers.SerializerMethodField('ingredient_name')
    measurement_unit = serializers.SerializerMethodField('ingredient_unit')

    def ingredient_unit(self, obj):
        return obj.measurement_unit.name

    def ingredient_name(self, obj):
        return obj.name.name

    class Meta:
        fields = ('__all__')
        model = IngredientUnit


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели, связывающей ингредиенты и рецепты."""

    id = serializers.SerializerMethodField('ingredient_id')
    name = serializers.SerializerMethodField('ingredient_name')
    measurement_unit = serializers.SerializerMethodField('ingredient_unit')

    def ingredient_id(self, obj):
        return obj.ingredient.id

    def ingredient_name(self, obj):
        return obj.ingredient.name

    def ingredient_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        fields = ('id, name, measurement_unit, amount')
        model = RecipeIngredient


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов, чтение."""

    tags = TagSerializer()
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer()

    class Meta:
        fields = ('__all__')
        model = Recipe
