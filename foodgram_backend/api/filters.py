"""Кастомные фильтры для поиска."""
from django_filters.rest_framework import (FilterSet, CharFilter,
                                           ModelMultipleChoiceFilter,
                                           BooleanFilter)

from recipes.models import Ingredients, Recipes, Tags


class IngredientFilter(FilterSet):
    """Кастомный фильтр для Ингредиентов."""

    name = CharFilter(method='filter_name')

    class Meta:
        model = Ingredients
        fields = ['name']

    def filter_name(self, queryset, name, value):
        queryset_starts_with = queryset.filter(name__istartswith=value)
        if queryset_starts_with.exists():
            return queryset_starts_with
        return queryset.filter(name__icontains=value)


class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe."""

    tags = ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )

    recipes_limit = CharFilter(method='recipes_limit')

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
