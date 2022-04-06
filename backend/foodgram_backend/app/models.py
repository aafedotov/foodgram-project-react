from users.models import CustomUser
from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime


class MeasurementUnit(models.Model):
    """Описание модели для единиц измерения ингредиентов."""

    name = models.CharField(max_length=50, unique=True,
                            verbose_name='Единица измерения',
                            help_text='Введите единицу измерения')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Описание модели для ингредиентов."""

    name = models.CharField(max_length=256, unique=True,
                            verbose_name='Название ингредиента',
                            help_text='Введите название')
    measurement_unit = models.ManyToManyField(MeasurementUnit,
                                 through='IngredientUnit',
                                 related_name='ingredients',
                                 verbose_name='Единицы измерения')

    def __str__(self):
        return self.name


class IngredientUnit(models.Model):
    """Промежуточная таблица ингредиентов и единиц измерения."""

    name = models.ForeignKey(Ingredient,
                             on_delete=models.CASCADE)
    measurement_unit = models.ForeignKey(MeasurementUnit,
                             on_delete=models.CASCADE)


class Subscription(models.Model):
    """Модель для подписок."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follows',
        verbose_name='Подписан на',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow'
            )
        ]


class Tag(models.Model):
    """Описание модели для тегов."""

    name = models.CharField(max_length=256, unique=True,
                            verbose_name='Имя тега',
                            help_text='Введите имя тега')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')
    color = models.CharField(max_length=7, unique=True,
                             verbose_name='Цвет', help_text='HEX-код')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная таблица для связи рецептов и ингредиентов."""

    ingredient = models.ForeignKey(
        IngredientUnit,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(validators=[MinValueValidator(1)],
                                 verbose_name='Количество')


class Recipe(models.Model):
    """Описание модели для рецептов."""

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    pub_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, verbose_name='Название рецепта',
                            help_text='Введите название рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Изображение')
    tag = models.ManyToManyField(Tag,
                                 related_name='recipes',
                                 through='RecipeTag',
                                 verbose_name='Теги')
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    ingredient = models.ManyToManyField(RecipeIngredient,
                                        related_name='recipes',
                                        verbose_name='Ингредиенты')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Промежуточная таблица для связи рецептов с тегами."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='tags'
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE
    )


class RecipeFavorite(models.Model):
    """Таблица для любимых рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                      related_name='users', verbose_name='Автор')
