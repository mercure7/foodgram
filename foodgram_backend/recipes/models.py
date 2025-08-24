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
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    tag = models.ManyToManyField('Tags', related_name='recipes',
                                 verbose_name='Теги')
    ingredients = models.ManyToManyField('Ingredients',
                                         through='RecipeIngredients',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')
    image = models.ImageField(verbose_name='Изображение блюда')

    class Meta:
        ordering = ['id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} от {self.author}'


class Ingredients(models.Model):
    """Модель для ингридиентов."""

    name = models.CharField(max_length=128,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=64,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ['id']
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

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[
        MinValueValidator(1, 'Минимальное количество ингредиента д.б. >= 1')
    ],
        verbose_name='Количество ингредиента в рецепте')

    class Meta:
        ordering = ['recipe']
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
