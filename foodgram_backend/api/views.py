from django.shortcuts import render, get_object_or_404
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
                          SubscriptionSerializer, AvatarUpdateSerializer
                          )
from .permissions import IsAuthorOrReadOnly


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    # Заменить пермишен IsAuthor or Readonly
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        recipes = [item.recipe for item in shopping_cart_items]
        
        # Собираем все ингредиенты из всех рецептов
        ingredients_dict = {}
        for recipe in recipes:
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
            'total_recipes': len(recipes)
        }
        
        return render(request, 'shopping_list.html', context)
    
        


    



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
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Добавление/удаление пользователя из подписок"""
        # recipe = self.get_object()
        follow_user = get_object_or_404(User, id=id)
        user = request.user
        
        subscription = Follow.objects.filter(user=user, following=follow_user)

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
        
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список подписок текущего пользователя"""
        subscriptions = Follow.objects.filter(
            user=request.user
        ).select_related('following')
        
        # Пагинация
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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


class AvatarViewset(viewsets.ModelViewSet):
    http_method_names = ['put']
    print('Здесь будет аватар')
