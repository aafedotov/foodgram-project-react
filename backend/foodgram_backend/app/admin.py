from django.contrib import admin

from .models import (
    Tag, Recipe, MeasurementUnit, IngredientUnit, Ingredient, Subscription,
    RecipeIngredient, RecipeTag, RecipeCart, RecipeFavorite
)


class RecipeAdmin(admin.ModelAdmin):
    """
    Администрирование рецептов.
    """

    readonly_fields = ('in_favorites',)
    # У рецепта должно быть название и автор рецепта
    list_display = ['author', 'name', 'in_favorites']
    # Рецепт можно искать по названию, автору и тегам
    search_fields = ['author__username', 'name', 'tag__name']
    empty_value_display = '-пусто-'

    # Должен быть столбец с отображением числа добавлений в избранное рецепта
    def in_favorites(self, obj):
        """Столбец с отображением числа добавлений в избранное рецепта."""
        return RecipeFavorite.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""

    list_display = ['show_name', 'show_unit']
    # Ингредиенты должно быть можно искать по названию
    search_fields = ['name__name']

    # У ингредиента должно отображаться название и единицы его измерения
    def show_name(self, obj):
        return obj.name.name

    def show_unit(self, obj):
        return obj.measurement_unit.name

# В админке должны быть модели:
# - ингредиенты
# - ингредиенты в рецептах
# - объекты избранного
# - объекты списка покупок
# - подписки
# - рецепты
# - теги
# У всех моделей должна быть возможность редактирования и удаления записей.

admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(MeasurementUnit)
admin.site.register(IngredientUnit, IngredientAdmin)
admin.site.register(Ingredient)
admin.site.register(Subscription)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(RecipeCart)
admin.site.register(RecipeFavorite)
