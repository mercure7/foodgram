import random
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer,
                                UserSerializer as BaseUserSerializer)

from recipes.models import Recipes, Ingredients, Tags, RecipeIngredients
from users.models import Follow
from .fields import Base64ImageField


User = get_user_model()


class TagsReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name', 'slug']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'avatar']


########################################################
class RecipeIngredientsWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id.id')
    name = serializers.CharField(source='ingredient_id.name')
    measurement_unit = serializers.CharField(
        source='ingredient_id.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientsSerializer(serializers.ModelSerializer):
    # amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']

    # def get_amount(self, data):
    #     return 'X'


##################################################################
class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    
    # ingredients = IngredientsSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsReadSerializer(many=True,
                                                  source='recipe_ingredients')
    tags = TagsReadSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time', 'is_in_shopping_cart',
                  'is_favorited']

######################################################
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False
##################################################


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = RecipeIngredientsWriteSerializer(many=True,
                                                   source='recipe_ingredients')
    # tags = TagsWriteSerializer(many=True, source='recipe_tags')
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    # # tags = serializers.PrimaryKeyRelatedField(
    #     queryset=Tags.objects.all(), 
    #     many=True, 
    #     required=False
    # )
    # author = UserSerializer(read_only=True)
    image = Base64ImageField()
    # author = serializers.SerializerMethodField()
    # original_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = ['id', 'author', 'tags', 'ingredients', 'name', 'text',
                  'image', 'cooking_time',]
        read_only_fields = ('author', )

    # def get_self_url(self, obj):
    #     request = self.context.get('request')
    #     if request and obj.pk:
    #         return request.build_absolute_uri(
    #             reverse('recipes', kwargs={'pk': obj.pk})
    #         )
        
    #      instance.object_url = f"{settings.BASE_URL}/api/recipes/{instance.id}/"
    #     return None

    # def get_author(self, obj):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         return request.user.id
    #     return None
    
    def create(self, validated_data):

        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        # instance = super().create(validated_data)

        # validated_data['original_url'] = f"{settings.BASE_URL}/recipes/{instance.id}/"
                
        recipe = Recipes.objects.create(**validated_data)

        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:

            ingredient_id = ingredient['ingredient_id']['id']
            ingredient_amount = ingredient['amount']

            RecipeIngredients.objects.create(
                recipe_id=recipe,
                ingredient_id=Ingredients.objects.get(id=ingredient_id),
                amount=ingredient_amount)
            
        # recipe_ingredients = []
        # for ingredient_data in ingredients:
        #     recipe_ingredients.append(
        #         RecipeIngredients(
        #             recipe=recipe,
        #             ingredient=ingredient_data['id'],
        #             amount=ingredient_data['amount']
        #         )
        #     )
        
        # RecipeIngredients.objects.bulk_create(recipe_ingredients)
        return recipe
        
    def update(self, instance, validated_data):
        # Обновляем основные поля
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        # Обновляем изображение, если предоставлено
        if 'image' in validated_data:
            instance.image = validated_data['image']

        instance.save()

        # Обновляем теги
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        
        # Обновляем ингредиенты
        if 'recipe_ingredients' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredients')

            # Удаляем старые ингредиенты
            instance.recipe_ingredients.all().delete()

            # Создаем новые
            for ingredient in ingredients_data:

                ingredient_id = ingredient['ingredient_id']['id']
                ingredient_amount = ingredient['amount']

                RecipeIngredients.objects.create(
                    recipe_id=instance,
                    ingredient_id=Ingredients.objects.get(id=ingredient_id),
                    amount=ingredient_amount)

        return instance


#############################################################
# Сериалиазаторы для работы с аутентификацией пользователей #
#############################################################
class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей"""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']


class UserGetSerializer(BaseUserSerializer):
    """ Сериализатор для получения пользователя/ползователей"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed']

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на этого автора"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user,
                following=obj
            ).exists()
        return False


##################################################
##################################################
##################################################


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с подписками на пользователей"""
    id = serializers.IntegerField(source='following.id')
    email = serializers.EmailField(source='following.email')
    username = serializers.CharField(source='following.username')
    first_name = serializers.CharField(source='following.first_name')
    last_name = serializers.CharField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        """Всегда True для подписок"""
        return True

    def get_recipes_count(self, obj):
        """Количество рецептов автора"""
        return obj.following.recipes.count()

    def get_recipes(self, obj):
        """Cписок рецептов автора"""
        recipes = obj.following.recipes.all()
        return recipes
      

class AvatarUpdateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ['avatar']

    # def validate_avatar(self, value):
    #     # Проверка размера файла (максимум 2MB)
    #     max_size = 2 * 1024 * 1024  # 2MB
    #     if value.size > max_size:
    #         raise serializers.ValidationError("Размер файла не должен превышать 2MB")
        
    #     # Проверка формата файла
    #     valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    #     import os
    #     ext = os.path.splitext(value.name)[1].lower()
    #     if ext not in valid_extensions:
    #         raise serializers.ValidationError(
    #             "Поддерживаются только JPG, JPEG, PNG и GIF файлы"
    #         )
        
    #     return value

    def update(self, instance, validated_data):
        # Удаляем старый аватар, если он существует
        if instance.avatar:
            instance.avatar.delete(save=False)
        
        instance.avatar = validated_data.get('avatar', None)
        instance.save()
        return instance
    
    # def destroy(self, instance, request, validated_data):
        
    #     if instance.avatar:
    #         instance.avatar.delete(save=False)
    #         instance.avatar = None
    #         instance.save()
    #         return instance


# class ShortLinkGetSerializer(serializers.ModelSerializer):

#     short_link = serializers.SlugRelatedField(slug_field='short_url', read_only=True)

#     class Meta:
#         model = Recipes
#         fields = ['short_link']