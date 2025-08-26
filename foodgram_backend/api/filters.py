from django_filters.rest_framework import (FilterSet, CharFilter,
                                           ModelMultipleChoiceFilter)

from recipes.models import Ingredients, Recipes, Tags


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ['name']


class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe."""

    tags = ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'author']
