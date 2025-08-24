from django.contrib import admin

from .models import (Recipes, Ingredients, Tags, RecipeIngredients,
                     ShoppingCart, Favorites)


admin.site.register(Recipes)
admin.site.register(Ingredients)
admin.site.register(Tags)
admin.site.register(RecipeIngredients)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
