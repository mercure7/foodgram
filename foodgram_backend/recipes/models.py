from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipes(models.Model):
    pass


class Ingredients(models.Model):
    pass


class Tag(models.Model):
    pass


class RecipeIngredients(models.Model):
    pass


class Favorites(models.Model):
    pass


class ShoppingCart(models.Model):
    pass
