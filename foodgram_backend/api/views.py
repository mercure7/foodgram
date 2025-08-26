from django.shortcuts import render
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters

from .filters import IngredientFilter, RecipeFilter
from recipes.models import Recipes, Tags, Ingredients
from .serializers import (RecipeReadSerializer, RecipePostSerializer,
                          TagsSerializer, IngredientsSerializer,
                          UserGetSerializer, UserSignUpSerializer
                          )


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [AllowAny,]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipePostSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # search_fields = ('^name',)
    filterset_class = IngredientFilter


class CustomUserViewset(DjoserUserViewSet):
    """Кастом вьюсет для создания пользователей"""
    pagination_class = LimitOffsetPagination
    
