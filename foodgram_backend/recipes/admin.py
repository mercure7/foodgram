from django.contrib import admin

from .models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                     ShoppingCart, Tags)


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    verbose_name_plural = 'Ингредиенты'


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    inlines = (IngredientsInline, )


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    inlines = [IngredientsInline,]
    list_display = (
        'name',
        'author',
        'display_tags',
        'pub_date',
        'short_url',
        'favorite_count',
        'display_ingredients'
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    empty_value_display = 'Значение не задано'
    readonly_fields = ('favorite_count', 'pub_date')

    @admin.display(description='Добавлен в избранное, кол-во раз')
    def favorite_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        """Отображает список ингредиентов."""
        return ", ".join(
            [ingredient.ingredient_id.name for ingredient
             in obj.recipe_ingredients.all()])

    @admin.display(description='Теги')
    def display_tags(self, obj):
        """Отображает список тегов."""
        return ", ".join([tag.name for tag in obj.tags.all()])


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)


admin.site.register(ShoppingCart)
admin.site.register(Favorites)
