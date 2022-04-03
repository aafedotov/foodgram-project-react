from django.contrib import admin

from .models import Tag, Recipe


class RecipeAdmin(admin.ModelAdmin):
    """
    Администрирование рецептов.
    """
    list_display = ['author', 'name', 'show_tags', 'show_ingredients']
    list_filter = ['name', 'author']
    search_fields = ['name', 'author']
    ordering = ['name']
    empty_value_display = '-пусто-'

    def show_tags(self, obj):
        return '\n'.join([item.name for item in obj.tag.all()])

    def show_ingredients(self, obj):
        return '\n'.join([item.name.name for item in obj.ingredient.all()])


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
