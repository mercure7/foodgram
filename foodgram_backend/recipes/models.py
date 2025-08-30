from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipes(models.Model):
    """Модель для рецептов."""

    name = models.CharField(max_length=256, verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Время приготовления должно быть >= 1 мин')
        ],
        verbose_name='Время приготовления, мин')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта',
                               related_name='recipes')
    tags = models.ManyToManyField('Tags',
                                  verbose_name='Теги',
                                  related_name='recipe_tags')

    ingredients = models.ManyToManyField('Ingredients',
                                         through='RecipeIngredients',
                                         through_fields=('recipe_id',
                                                         'ingredient_id'),
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Изображение блюда')
    pub_date = models.DateTimeField(auto_now_add=True)
    original_url = models.URLField(unique=True, null=True, blank=True)
    short_url = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} от {self.author}'


class Ingredients(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(max_length=128,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=64,
                                        verbose_name='Единица измерения')

    class Meta:
        # ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tags(models.Model):
    """Модель для тегов."""

    name = models.CharField(max_length=32, unique=True,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=32, unique=True, null=True,
                            verbose_name='Слаг тега')

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}, {self.slug}'


class RecipeIngredients(models.Model):
    """Промежуточная модель для ингредиентов в рецептах."""

    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                                  related_name='recipe_ingredients')
    ingredient_id = models.ForeignKey(Ingredients, on_delete=models.CASCADE,
                                      related_name='ingredient_recipes')
    amount = models.PositiveIntegerField(validators=[
        MinValueValidator(1, 'Минимальное количество ингредиента д.б. >= 1')
    ],
        verbose_name='Количество ингредиента в рецепте')

    class Meta:
        ordering = ['recipe_id']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class Favorites(models.Model):
    """Модель для рецептов в избранном."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        ordering = ['user']
        unique_together = ['user', 'recipe']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        ordering = ['user']
        verbose_name = 'Корзина для покупок'
        verbose_name_plural = 'Корзина для покупок'
        unique_together = ['user', 'recipe']
