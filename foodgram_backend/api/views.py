import random
import string

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from constants import SHORT_CODE_LENGTH
from recipes.models import Favorites, Ingredients, Recipes, ShoppingCart, Tags

from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarUpdateSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientsSerializer,
                          RecipePostSerializer, RecipeReadSerializer,
                          RecipeReadSerializerForSubscriptions,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagsReadSerializer, UserGetSerializerFollow)

User = get_user_model()


def generate_short_code():
    """Генерирует произвольный слаг для прямой ссылки."""
    short_url = ''.join(random.choices(string.ascii_letters
                        + string.digits, k=SHORT_CODE_LENGTH))
    if not Recipes.objects.filter(short_url=short_url).exists():
        return short_url
    return generate_short_code()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthorOrReadOnly()]
        elif self.action in ['create', 'favorite', 'shopping_cart',
                             'download_shopping_cart']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        short_url=generate_short_code())

    def create_favorites_shopping_cart(self, serializer, obj):
        serializer_read = RecipeReadSerializerForSubscriptions(obj)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer_read.data,
                            status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete_favorites_shopping_cart(self, obj, error):
        deleted = obj.delete()
        if deleted[0] != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': f'{error}'},
                        status=status.HTTP_400_BAD_REQUEST
                        )

    @action(detail=True, methods=['post', 'delete'],)
    def favorite(self, request, id=None):
        """Добавление/удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipes, id=id)
        user = request.user

        favorite = Favorites.objects.filter(user=user, recipe=recipe)
        data = {'recipe': recipe.id, 'user': user.id}
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request})

        if request.method == 'POST':
            return self.create_favorites_shopping_cart(serializer, recipe)
        return self.delete_favorites_shopping_cart(
            favorite, error='Рецепт не в избранном!')

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, id=None):
        """Добавление/удаление рецепта из корзины покупок."""
        recipe = get_object_or_404(Recipes, id=id)
        user = request.user
        recipe_in_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        data = {'recipe': recipe.id, 'user': user.id}
        serializer = ShoppingCartSerializer(data=data,
                                            context={'request': request})

        if request.method == 'POST':
            return self.create_favorites_shopping_cart(serializer, recipe)
        return self.delete_favorites_shopping_cart(
            recipe_in_cart,
       error='Рецепт не в корзине!')

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user

        shopping_cart_recipes = ShoppingCart.objects.filter(user=user)

        shopping_cart_ingredients = (
            ShoppingCart.objects.filter(user=user).values(
                name=F('recipe__recipe_ingredients__ingredient_id__name'),
                unit=F(
                    'recipe__recipe_ingredients__'
                    'ingredient_id__measurement_unit'
                )
            ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount')
                       ).order_by('name')
        )

        context = {
            'ingredients': shopping_cart_ingredients,
            'user': user,
            'total_recipes': len(shopping_cart_recipes)
        }

        return render(request, 'shopping_list.html', context)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, id=None):
        """Получить короткую ссылку для конкретного рецепта."""
        recipe = get_object_or_404(Recipes, id=id)
        return Response({
            'short-link': request.build_absolute_uri(f'/s/{recipe.short_url}/')
        })


class TagViewset(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TagsReadSerializer
    pagination_class = None
    http_method_names = ['get']


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    permission_classes = [AllowAny, ]
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    http_method_names = ['get']


class UserViewset(DjoserUserViewSet):
    """Кастом вьюсет для создания пользователей."""

    pagination_class = PageLimitPagination
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [CurrentUserOrAdmin()]
        elif self.action in ['subscribe', 'get_subscriptions', 'avatar', 'me']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Получение и обновление данных текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Добавление/удаление пользователя из подписок."""
        if not request.user.is_authenticated:
            return Response(
                {'ошибка': 'Пользователь не авторизован'},
                status=status.HTTP_401_UNAUTHORIZED)

        follow_user = get_object_or_404(User, id=id)
        user = request.user
        subscription = user.follower.filter(following=follow_user)
        data = {'user': user.id, 'following': follow_user.id}
        query_params = request.query_params.get('recipes_limit')
        serializer = FollowSerializer(data=data)

        if request.method == 'POST':
            serializer_read = UserGetSerializerFollow(
                follow_user,
                context={'recipes_limit': query_params})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer_read.data,
                                status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        deleted = subscription.delete()
        if deleted[0] != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Пользователь не в подписках!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            pagination_class=PageLimitPagination,
            url_path='subscriptions'
            )
    def get_subscriptions(self, request):
        """Список подписок текущего пользователя."""
        user = request.user
        subscriptions = user.follower.all()
        subscribed_users = [item.following for item in subscriptions]
        query_params = request.query_params.get('recipes_limit')

        paginated_subscribed_users = self.paginate_queryset(subscribed_users)
        if paginated_subscribed_users is not None:
            serializer = SubscriptionSerializer(
                paginated_subscribed_users,
                many=True,
                context={'recipes_limit': query_params})

            return self.get_paginated_response(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='me/avatar', methods=['put', 'delete'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Обновление и удаление аватара текущего пользователя."""
        user = request.user
        serializer = AvatarUpdateSerializer(user, data=request.data)
        if request.method == 'PUT' and serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Аватар не найден!'},
                        status=status.HTTP_400_BAD_REQUEST)


def redirect_short_link(request, code):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipes, short_url=code)
        return redirect(request.build_absolute_uri(f'/recipes/{recipe.id}'))
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
