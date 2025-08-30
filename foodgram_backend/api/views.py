import random
import string
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.template.loader import render_to_string
from django.http import HttpResponse

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework import filters

from .filters import IngredientFilter, RecipeFilter
from recipes.models import Recipes, Tags, Ingredients, Favorites, ShoppingCart
from users.models import Follow
from .serializers import (RecipeReadSerializer, RecipePostSerializer,
                          IngredientsSerializer, TagsReadSerializer,
                          UserGetSerializer, UserSignUpSerializer,
                          SubscriptionSerializer, AvatarUpdateSerializer,
                          )
from .permissions import IsAuthorOrReadOnly
from .pagination import PageLimitPagination

SHORT_CODE_LENGTH = 6

User = get_user_model()


def generate_short_code():

    short_url = ''.join(random.choices(string.ascii_letters
                        + string.digits, k=SHORT_CODE_LENGTH))
    if not Recipes.objects.filter(short_url=short_url).exists():
        return short_url
    return generate_short_code()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    # Заменить пермишен IsAuthor or Readonly
    permission_classes = [AllowAny,]

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'
    pagination_class = PageLimitPagination

    # def generate_short_code(self):

    #     short_url = ''.join(random.choices(string.ascii_letters
    #                         + string.digits, k=SHORT_CODE_LENGTH))
    #     if not Recipes.objects.filter(short_url=short_url).exists():
    #         return short_url
    #     return self.generate_short_code()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, 
                        short_url=generate_short_code(),
                        )
        
        # instance.original_url = f"{settings.BASE_URL}/recipes/{instance.id}/"

        # serializer.save(update_fields=['original_url'])
    


    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthorOrReadOnly])
    def favorite(self, request, id=None):
        """Добавление/удаление рецепта из избранного"""
        # recipe = self.get_object()
        recipe = get_object_or_404(Recipes, id=id)
        user = request.user
        
        favorites = Favorites.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if favorites.exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(user=user, recipe=recipe)
            return Response(
                {'message': 'Рецепт добавлен в избранное'},
                status=status.HTTP_201_CREATED
            )
        
        elif request.method == 'DELETE':
            
            if not favorites.exists():
                return Response(
                    {'errors': 'Рецепт не в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorites.delete()
            return Response(
                {'message': 'Рецепт удален из избранного'},
                status=status.HTTP_204_NO_CONTENT
            )
        
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthorOrReadOnly])
    def shopping_cart(self, request, id=None):
        """Добавление/удаление рецепта из корзины покупок"""
        recipe = get_object_or_404(Recipes, id=id)
        user = request.user
        recipe_in_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if recipe_in_cart.exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                {'message': 'Рецепт добавлен в корзину'},
                status=status.HTTP_201_CREATED
            )
        
        elif request.method == 'DELETE':
            
            if not recipe_in_cart.exists():
                return Response(
                    {'errors': 'Рецепта нет в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_in_cart.delete()
            return Response(
                {'message': 'Рецепт удален из корзины покупок'},
                status=status.HTTP_204_NO_CONTENT
            )
    # @action(detail=False, methods=['get'],
    #         permission_classes=[IsAuthenticated])
    # def download_shopping_cart(self, request):
    #     user = request.user
    #     recipe_in_cart = ShoppingCart.objects.filter(user=user)
    #     recipes = recipe_in_cart.recipe.all()

    #     context = {'recipes': recipes,
    #                }

    #     return render(request, 'shopping_list.html', context, status)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        
        # Получаем рецепты из корзины пользователя
        recipes_in_cart = []
        shopping_cart_recipes = ShoppingCart.objects.filter(user=user)
        recipes_in_cart = [recipe.recipe for recipe in shopping_cart_recipes]
        
        # Собираем все ингредиенты из всех рецептов
        ingredients_dict = {}
        for recipe in recipes_in_cart:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient_id
                key = (ingredient.name, ingredient.measurement_unit)
                if key in ingredients_dict:
                    ingredients_dict[key] += recipe_ingredient.amount
                else:
                    ingredients_dict[key] = recipe_ingredient.amount
        
        # Преобразуем в список для шаблона
        ingredients_list = [
            {
                'name': name,
                'measurement_unit': unit,
                'total_amount': amount
            }
            for (name, unit), amount in ingredients_dict.items()
        ]

        context = {
            'ingredients': ingredients_list,
            'user': user,
            'total_recipes': len(recipes_in_cart)
        }

        return render(request, 'shopping_list.html', context)
    
    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, id=None):
        """Получить короткую ссылку для конкретного рецепта"""
        recipe = get_object_or_404(Recipes, id=id)
        return Response({
            'short-link': request.build_absolute_uri(f'/s/{recipe.short_url}/')
        })


class TagViewset(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = TagsReadSerializer
    pagination_class = None


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = IngredientFilter


# class FavoriteViewset(viewsets.ModelViewSet):
#     queryset = Favorites.objects.all()
#     permission_classes = [IsAuthenticated]
#     def get_queryset(self):
#         recipe = get_object_or_404(Recipes, id=self.kwargs.get('id'))
#         return recipe.favorites.all()


######################################################
class CustomUserViewset(DjoserUserViewSet):
    """Кастом вьюсет для создания пользователей"""
    pagination_class = PageLimitPagination
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        
        # Явно передаем КОНКРЕТНЫЕ параметры, а не весь request
        context['recipes_limit'] = self.request.GET.get('recipes_limit', 10)
        print(context['recipes_limit'])        
        return context

    

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Добавление/удаление пользователя из подписок"""
        # recipe = self.get_object()
        follow_user = get_object_or_404(User, id=id)
        user = request.user

        # subscription = Follow.objects.filter(user=user, following=follow_user)
        subscription = user.follower.filter(following=follow_user)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'errors': 'Этот пользователь уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, following=follow_user)
            return Response(
                {'message': 'Пользватель добавлен в подписки'},
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':

            if not subscription.exists():
                return Response(
                    {'errors': 'Пользователь не в подписках'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(
                {'message': 'Пользователь удален из подписок'},
                status=status.HTTP_204_NO_CONTENT)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ИСПРАВИТЬ!!!
#################################################################
#################################################################

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            pagination_class=PageLimitPagination,
            url_path='subscriptions'
            )
    def get_subscriptions(self, request):
        """Список подписок текущего пользователя"""
        
        user = request.user
        
        subscriptions = user.follower.all()

        subscribed_users = [item.following for item in subscriptions]

        # subscribed_users = User.objects.filter(id__in=subscribed_users_id)

        query_params = request.query_params.get('recipes_limit')
        
        # subscriptions = Follow.objects.filter(user=user)
        # ).select_related('following')

        # Пагинация
        paginated_subscribed_users = self.paginate_queryset(subscribed_users)
        if paginated_subscribed_users is not None:
            serializer = SubscriptionSerializer(paginated_subscribed_users, many=True, context={'recipes_limit': query_params})
            return self.get_paginated_response(serializer.data)

        # serializer = SubscriptionSerializer(subscribed_users, context={'recipes_limit': query_params}, many=True)
     
        return Response(serializer.data, status=status.HTTP_200_OK)
    
##############################################################################
    @action(detail=False, url_path='me/avatar', methods=['put', 'delete'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Обновление и удаление аватара текущего пользователя"""

        user = request.user
        serializer = AvatarUpdateSerializer(user, data=request.data)
        if request.method == 'PUT' and serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if user.avatar and request.method == 'DELETE':
            user.avatar.delete(save=False)  
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class Subscribtions(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated,]
    parser_classes = [LimitOffsetPagination,]


# class ShortLinkGetViewset(viewsets.ModelViewSet):
#     serializer_class = ShortLinkGetSerializer
#     permission_classes = [AllowAny]
#     pagination_class = None

#     def get_queryset(self):
#         # Если хотите фильтровать по recipe_id из URL параметров
#         recipe_id = self.kwargs.get('recipe_id')
#         return get_object_or_404(Recipes, id=recipe_id)


def redirect_short_link(request, code):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipes, short_url=code)
        return redirect(request.build_absolute_uri(f'/recipes/{recipe.id}/'))
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
