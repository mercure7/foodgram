import django_filters 

from recipes.models import Ingredients, Recipes


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для модели Recipe."""
    tags = django_filters.CharFilter(field_name='tags__slug',
                                     lookup_expr='iexact')

    class Meta:
        model = Recipes
        fields = ['tags', 'author']
