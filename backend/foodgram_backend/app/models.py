from users.models import CustomUser
from django.db import models
from django.core.validators import MinValueValidator


class MeasurementUnit(models.Model):
    """Описание модели для единиц измерения ингредиентов."""

    name = models.CharField(max_length=50, unique=True,
                            verbose_name='Единица измерения',
                            help_text='Введите единицу измерения:')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Описание модели для ингредиентов."""

    name = models.CharField(max_length=256, unique=True,
                            verbose_name='Название ингредиента',
                            help_text='Введите название:')
    measurement_unit = models.ManyToManyField(MeasurementUnit,
                                 related_name='ingredients',
                                 verbose_name='Единицы измерения')

    def __str__(self):
        return self.name


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
                            help_text='Введите имя тега:')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')
    color = models.CharField(max_length=7, unique=True,
                             verbose_name='Цвет', help_text='HEX-код:')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Описание модели для рецептов."""

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    name = models.CharField(max_length=200, verbose_name='Название рецепта',
                            help_text='Введите название рецепта:')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Изображение')
    tag = models.ManyToManyField(Tag,
                                 related_name='recipes',
                                 through='RecipeTag',
                                 verbose_name='Теги')
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    ingredient = models.ManyToManyField(Ingredient,
                                        related_name='recipes',
                                        through='RecipeIngredient',
                                        verbose_name='Ингредиенты')

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Промежуточная таблица для связи рецептов с тегами."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE
    )


class RecipeIngredient(models.Model):
    """Промежуточная таблица для связи рецептов и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(validators=[MinValueValidator(1)],
                                 verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]
