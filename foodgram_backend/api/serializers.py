from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer,
                                UserSerializer as BaseUserSerializer,
                                
                                )

from recipes.models import Recipes, Ingredients, Tags, RecipeIngredients
from .fields import Base64ImageField


User = get_user_model()


class RecipeIngredientsSerialier(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']


class IngredientsSerializer(serializers.ModelSerializer):
    # amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']

    # def get_amount(self, data):
    #     return 'X'


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name', 'slug']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'avatar']


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    ingredients = IngredientsSerializer(many=True)
    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time']


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = RecipeIngredientsSerialier(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    author = User.objects.get(id=1)

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time']


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей"""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']


class UserGetSerializer(BaseUserSerializer):
    """ Сериализатор для получения пользователя/ползователей"""

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'avatar']
