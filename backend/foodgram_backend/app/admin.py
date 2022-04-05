from django.contrib import admin

from .models import Tag, Recipe


class RecipeAdmin(admin.ModelAdmin):
    """
    Администрирование рецептов.
    """
    list_display = ['author', 'show_tags', 'show_ingredients']
    list_filter = ['author']
    search_fields = ['author']
    ordering = ['author']
    empty_value_display = '-пусто-'

    def show_tags(self, obj):
        return '\n'.join([item.name for item in obj.tag.all()])

    def show_ingredients(self, obj):
        return '\n'.join([item.ingredient.name.name for item in obj.ingredient.all()])


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
