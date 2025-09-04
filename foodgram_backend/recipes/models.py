from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from constants import (MAX_LENGTH_INGREDIENT_NAME,
                       MAX_LENGTH_MEAS_UNIT_INGREDIENT, MAX_LENGTH_RECIPE_NAME,
                       MAX_LENGTH_TAG_NAME, MAX_LENGTH_TAG_SLUG,
                       MIN_COOKING_TIME_VALUE)

User = get_user_model()


class Recipes(models.Model):
    """Модель для рецептов."""

    name = models.CharField(max_length=MAX_LENGTH_RECIPE_NAME,
                            verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME_VALUE,
                              'Время приготовления должно быть >= 1 мин')
        ],
        verbose_name='Время приготовления, мин')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта',
                               )
    tags = models.ManyToManyField('Tags',
                                  verbose_name='Теги',
                                  related_name='recipe_tags')
    ingredients = models.ManyToManyField('Ingredients',
                                         through='RecipeIngredients',
                                         through_fields=('recipe_id',
                                                         'ingredient_id'),
                                         verbose_name='Ингредиенты')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Изображение блюда')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    original_url = models.URLField(unique=True, null=True, blank=True)
    short_url = models.SlugField(unique=True, null=True, blank=True,
                                 verbose_name='Слаг для прямой ссылки')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name} от {self.author}'


class Ingredients(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(max_length=MAX_LENGTH_INGREDIENT_NAME,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEAS_UNIT_INGREDIENT,
        verbose_name='Единица измерения')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ['name', 'measurement_unit']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tags(models.Model):
    """Модель для тегов."""

    name = models.CharField(max_length=MAX_LENGTH_TAG_NAME, unique=True,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=MAX_LENGTH_TAG_SLUG, unique=True,
                            null=True, verbose_name='Слаг тега')

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}, {self.slug}'


class RecipeIngredients(models.Model):
    """Промежуточная модель для ингредиентов в рецептах."""

    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                                  related_name='recipe_ingredients',
                                  verbose_name='Рецепт')
    ingredient_id = models.ForeignKey(Ingredients, on_delete=models.CASCADE,
                                      related_name='ingredient_recipes',
                                      verbose_name='Название ингредиента')
    amount = models.PositiveIntegerField(validators=[
        MinValueValidator(1, 'Минимальное количество ингредиента д.б. >= 1')
    ],
        verbose_name='Количество ингредиента в рецепте')

    class Meta:
        ordering = ['recipe_id']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        unique_together = ['recipe_id', 'ingredient_id']

    def __str__(self):
        return f'{self.recipe_id}, {self.ingredient_id}'


class FavoriteShoppingCartBaseModel(models.Model):
    """Базовая модель для рецептов в избранном и списка покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)

    class Meta:
        ordering = ['user']
        unique_together = ['user', 'recipe']
        abstract = True

    def __str__(self):
        return f'{self.user}, {self.recipe}'


class Favorites(FavoriteShoppingCartBaseModel):
    """Модель для рецептов в избранном."""

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'


class ShoppingCart(FavoriteShoppingCartBaseModel):
    """Модель для списка покупок."""

    class Meta:
        verbose_name = 'Корзина для покупок'
        verbose_name_plural = 'Корзина для покупок'
        default_related_name = 'shopping_cart'
