from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField

from app.models import (
    Tag, Ingredient, MeasurementUnit, IngredientUnit, RecipeIngredient,
    Recipe, RecipeTag, Subscription, RecipeFavorite, RecipeCart
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели пользователя."""

    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField('subscribed_check')

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

    def subscribed_check(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
            if isinstance(user, User):
                return Subscription.objects.filter(
                    user=user, following=obj
                ).exists()
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


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для эндпоинта смены пароля пользователя."""

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        fields = ('__all__')
        model = Tag


class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов-рецептов."""

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

    name = serializers.CharField(source='name.name')
    measurement_unit = serializers.CharField(source='measurement_unit.name')

    class Meta:
        fields = ('__all__')
        model = IngredientUnit


class RecipeReadIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели, связывающей ингредиенты и рецепты."""

    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = RecipeIngredient


class RecipePostIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели, связывающей ингредиенты и рецепты."""

    id = PrimaryKeyRelatedField(queryset=IngredientUnit.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов, чтение."""

    tags = TagSerializer(many=True, read_only=True, source='tag')
    author = UserSerializer()
    ingredients = RecipeReadIngredientSerializer(
        many=True, read_only=True, source='ingredient'
    )
    image = serializers.SerializerMethodField('image_url')
    is_favorited = serializers.SerializerMethodField('favorited_check')
    is_in_shopping_cart = serializers.SerializerMethodField('cart_check')

    class Meta:
        fields = ('tags', 'author', 'ingredients', 'name', 'text', 'image',
                  'cooking_time', 'id', 'is_favorited', 'is_in_shopping_cart')
        model = Recipe

    def cart_check(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
            if isinstance(user, User):
                return RecipeCart.objects.filter(
                    user=user,
                    recipe=obj
                ).exists()
        return False

    def favorited_check(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
            if isinstance(user, User):
                return RecipeFavorite.objects.filter(
                    user=user,
                    recipe=obj
                ).exists()
        return False

    def image_url(self, obj):
        return '/media/' + str(obj.image)


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов, изменение."""

    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    author = SlugRelatedField(slug_field='username',
                              default=serializers.CurrentUserDefault(),
                              read_only=True)
    ingredients = RecipePostIngredientSerializer(
        many=True,
        source='ingredient'
    )

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

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient')
        tags_data = validated_data.pop('tags')
        super().update(instance, validated_data)
        recipe = instance
        recipe.ingredient.select_related().all().delete()
        RecipeTag.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients_data:
            ing = RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
            recipe.ingredient.add(ing)
        for tag in tags_data:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        return recipe

    class Meta:
        fields = (
            'ingredients', 'tags', 'image', 'author', 'text',
            'cooking_time', 'name'
        )
        model = Recipe


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для рецептов в подписках."""

    image = serializers.SerializerMethodField('image_url')

    def image_url(self, obj):
        return '/media/' + str(obj.image)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeListSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField('subscribed_check')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            queryset = obj.recipes.all()[:recipes_limit]
        else:
            queryset = obj.recipes.all()
        serializer = SubscribeRecipeSerializer(queryset, many=True)
        return serializer.data

    def subscribed_check(self, obj):
        return True

    class Meta:

        fields = ['id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'recipes',
                  'recipes_count',
                  'is_subscribed'
                  ]
        model = User
