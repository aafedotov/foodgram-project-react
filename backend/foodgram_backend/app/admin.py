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
    list_display = ['author', 'name', 'in_favorites']
    list_filter = ['author', 'name', 'tag']
    empty_value_display = '-пусто-'

    def in_favorites(self, obj):
        return RecipeFavorite.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""

    list_display = ['show_name', 'show_unit']
    # list_filter = ['show_name']

    def show_name(self, obj):
        return obj.name.name

    def show_unit(self, obj):
        return obj.measurement_unit.name


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
