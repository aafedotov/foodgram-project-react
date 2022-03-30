import django_filters
from django_filters import rest_framework as filters

from app.models import IngredientUnit


class IngredientFilter(filters.FilterSet):
    """Кастомный фильтр для модели Ingredient."""

    name = django_filters.CharFilter(
        field_name='name__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = IngredientUnit
        fields = ('name',)
