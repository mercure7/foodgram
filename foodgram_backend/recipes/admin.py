from django.contrib import admin

from .models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                     ShoppingCart, Tags)


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'display_tags',
        'image',
        'pub_date',
        'short_url',
        'favorite_count'
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    empty_value_display = 'Значение не задано'
    readonly_fields = ('favorite_count', 'pub_date')

    def favorite_count(self, obj):
        return obj.favorites.count()

    favorite_count.short_description = 'Добавлен в избранное, кол-во раз'

    def display_ingredients(self, obj):
        """Отображает список ингредиентов."""
        return ", ".join(
            [ingredient.name for ingredient in obj.recipe_ingredients.all()])
    display_ingredients.short_description = 'Ингредиенты'

    def display_tags(self, obj):
        """Отображает список тегов."""
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(RecipeIngredients)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
