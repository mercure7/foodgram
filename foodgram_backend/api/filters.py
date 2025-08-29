from django_filters.rest_framework import (FilterSet, CharFilter,
                                           ModelMultipleChoiceFilter,
                                           BooleanFilter)
from django.db.models import Q
from django.db.models import QuerySet

from recipes.models import Ingredients, Recipes, Tags


class IngredientFilter(FilterSet):
    # name = CharFilter(lookup_expr='istartswith')
    name = CharFilter(method='filter_name')

    class Meta:
        model = Ingredients
        fields = ['name']

    # Добавляем поиск по наличию символов не только в начале
    def filter_name(self, queryset, name, value):
        # # Ищем по началу, но если нет результатов - ищем по содержанию
        # if queryset.filter(name__istartwith=value).exists():
        #     return queryset
        # return queryset.filter(name__icontains=value)

        queryset = queryset.filter(Q(name__istartswith=value) 
                                   | Q(name__icontains=value))
        return queryset
        

class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe."""

    tags = ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    ### ПРОВЕРИТЬ ЭТОТ ВАРИАНТ
    # tags = filters.AllValuesMultipleFilter(
    #     field_name='tags__slug',
    #     label='Tags'

    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )

    recipes_limit = CharFilter(method='recipes_limit')

    class Meta:
        model = Recipes
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited', 
                  'recipes_limit']

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
    
    def filter_recipes_limit(self, queryset, name, value):
        return queryset[0:value]
