import django_filters
from django_filters import rest_framework as filters

from app.models import IngredientUnit, Recipe


class IngredientFilter(filters.FilterSet):
    """Кастомный фильтр для модели Ingredient."""

    name = django_filters.CharFilter(
        field_name='name__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = IngredientUnit
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для модели Recipe."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tag__slug'
    )
    author = django_filters.AllValuesFilter(
        field_name='author__id'
    )
    is_favorited = django_filters.BooleanFilter()


    class Meta:
        model = Recipe
        fields = ('tag',)
