from rest_framework import serializers

from django.contrib.auth import get_user_model
from app.models import (
    Tag, Ingredient, MeasurementUnit, IngredientUnit, RecipeIngredient,
    Recipe, RecipeTag, Subscription
)

from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели пользователя."""

    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField('subscribed_check')

    def subscribed_check(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
            if isinstance(user, User):
                return Subscription.objects.filter(user=user, following=obj).exists()
        return False

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
                  'is_subscribed'
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


class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов-рецептов."""

    # tag = TagSerializer(many=True)
    class Meta:
        fields = ('__all__')
        model = RecipeTag


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


class RecipeReadIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели, связывающей ингредиенты и рецепты."""

    id = serializers.SerializerMethodField('ingredient_id')
    name = serializers.SerializerMethodField('ingredient_name')
    measurement_unit = serializers.SerializerMethodField('ingredient_unit')

    def ingredient_id(self, obj):
        return obj.ingredient.id

    def ingredient_name(self, obj):
        return obj.ingredient.name.name

    def ingredient_unit(self, obj):
        return obj.ingredient.measurement_unit.name

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = RecipeIngredient


class RecipePostIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели, связывающей ингредиенты и рецепты."""

    id = PrimaryKeyRelatedField(queryset=IngredientUnit.objects.all())
    #
    # def ingredient_id(self, obj):
    #     return obj.ingredient.id

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов, чтение."""

    tags = TagSerializer(many=True, read_only=True, source='tag')
    author = UserSerializer()
    ingredients = RecipeReadIngredientSerializer(many=True, read_only=True, source='ingredient')
    image = serializers.SerializerMethodField('image_url')

    def image_url(self, obj):
         return '/media/' + str(obj.image)

    class Meta:
        fields = ('tags', 'author', 'ingredients', 'name', 'text', 'image',
                  'cooking_time', 'id')
        model = Recipe


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов, изменение."""

    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    author = SlugRelatedField(slug_field='username',
                              default=serializers.CurrentUserDefault(),
                              read_only=True)
    ingredients = RecipePostIngredientSerializer(many=True, source='ingredient')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            ing = RecipeIngredient.objects.create(
                                            ingredient=ingredient['id'],
                                            amount=ingredient['amount'])
            recipe.ingredient.add(ing)
        for tag in tags_data:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        return recipe

    class Meta:
        fields = ('ingredients', 'tags', 'image', 'author', 'text', 'cooking_time', 'name')
        model = Recipe


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField('image_url')

    def image_url(self, obj):
         return '/media/' + str(obj.image)

    class Meta:

        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeListSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    recipes = SubscribeRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField('count_recipes')

    # def recipes_list(self, obj):
    #     return SubscribeRecipeSerializer(obj.recipes.all())

    def count_recipes(self, obj):
        return obj.recipes.all().count()


    class Meta:

        fields = ['id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'recipes',
                  'recipes_count'
                  ]
        model = User

