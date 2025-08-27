from django_filters.rest_framework import (FilterSet, CharFilter,
                                           ModelMultipleChoiceFilter,
                                           BooleanFilter)

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

    # tags = filters.AllValuesMultipleFilter(
    #     field_name='tags__slug',
    #     label='Tags'

    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset
