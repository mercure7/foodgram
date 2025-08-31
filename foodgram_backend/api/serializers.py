from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from djoser.serializers import (UserCreateSerializer,
                                UserSerializer as BaseUserSerializer)

from recipes.models import Recipes, Ingredients, Tags, RecipeIngredients
from .fields import Base64ImageField


User = get_user_model()


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'password']


class UserGetSerializer(BaseUserSerializer):
    """Сериализатор для получения пользователя/пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed']

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на этого автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class TagsReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name', 'slug']


class RecipeIngredientsWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id.id', required=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']

    def validate_id(self, value):
        if not Ingredients.objects.filter(id=value).exists():
            raise serializers.ValidationError('Нет такого ингредиента!')
        return value

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!')
        return value


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id.id')
    name = serializers.CharField(source='ingredient_id.name')
    measurement_unit = serializers.CharField(
        source='ingredient_id.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    ingredients = RecipeIngredientsReadSerializer(many=True,
                                                  source='recipe_ingredients')
    tags = TagsReadSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time']

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


class RecipeReadSerializerForSubscriptions(RecipeReadSerializer):

    class Meta(RecipeReadSerializer.Meta):
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = RecipeIngredientsWriteSerializer(many=True,
                                                   source='recipe_ingredients',
                                                   required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True, required=True)
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time']
        read_only_fields = ('author', )

    def validate_tags(self, value):
        if value is None:
            raise ValidationError("Поле тегов обязательно для заполнения")
        if value == []:
            raise ValidationError("Теги не должны быть пустыми")
        if len(value) != len(set(value)):
            raise ValidationError("Теги не должны содержать дубликатов")
        return value

    def validate_ingredients(self, value):
        print(value)
        if value is None:
            raise ValidationError(
                "Поле ингредиентов обязательно для заполнения")
        if value == []:
            raise ValidationError("Нужно добавить ингредиенты")
        ingredient_ids = []
        for ingredient in value:
            ingredient_ids.append(ingredient.get('ingredient_id').get('id'))
            print(ingredient_ids)
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Найдены дубликаты ингредиенты')
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if self.context['request'].method == 'PATCH':
            data = request.data
            if 'tags' not in data:
                raise serializers.ValidationError({
                    'tags': 'Это поле обязательно для обновления'
                })
            if 'ingredients' not in data:
                raise serializers.ValidationError({
                    'ingredients': 'Это поле обязательно для обновления'
                })
        return attrs

    def to_representation(self, instance):
        """Преобразуем IDs в объекты при выводе."""
        representation = super().to_representation(instance)
        representation['tags'] = TagsReadSerializer(
            instance.tags.all(),
            many=True
        ).data
        representation['ingredients'] = RecipeIngredientsReadSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data
        representation['author'] = UserGetSerializer(
            instance.author,
            many=False
        ).data
        return representation

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

    def create(self, validated_data):

        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:
            ingredient_id = ingredient['ingredient_id']['id']
            ingredient_amount = ingredient['amount']
            RecipeIngredients.objects.create(
                recipe_id=recipe,
                ingredient_id=Ingredients.objects.get(id=ingredient_id),
                amount=ingredient_amount)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        if 'recipe_ingredients' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredients')

            instance.recipe_ingredients.all().delete()

            for ingredient in ingredients_data:
                ingredient_id = ingredient['ingredient_id']['id']
                ingredient_amount = ingredient['amount']

                RecipeIngredients.objects.create(
                    recipe_id=instance,
                    ingredient_id=Ingredients.objects.get(id=ingredient_id),
                    amount=ingredient_amount)
        return instance


class SubscriptionSerializer(UserGetSerializer):
    """Сериализатор для работы с подписками на пользователей."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserGetSerializer.Meta):
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar']

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Cписок рецептов автора."""
        recipes_limit = self.context.get('recipes_limit')

        if recipes_limit is not None:
            recipes_to_show = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes_to_show = obj.recipes.all()

        return RecipeReadSerializerForSubscriptions(recipes_to_show,
                                                    many=True).data


class AvatarUpdateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        if instance.avatar:
            instance.avatar.delete(save=False)
        instance.avatar = validated_data.get('avatar', None)
        instance.save()
        return instance
