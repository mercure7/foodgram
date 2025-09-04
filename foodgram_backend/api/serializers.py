from constants import MIN_VALUE_INGREDIENT
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from recipes.models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                            ShoppingCart, Tags)
from rest_framework import serializers
from rest_framework.serializers import UniqueTogetherValidator, ValidationError
from users.models import Follow

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
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar']

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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    amount = serializers.IntegerField(required=True,
                                      min_value=MIN_VALUE_INGREDIENT)

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']

    def validate_id(self, value):
        if not Ingredients.objects.filter(id=value.id).exists():
            raise serializers.ValidationError('Нет такого ингредиента!')
        return value


class RecipeIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(source='ingredient_id.name')
    measurement_unit = serializers.CharField(
        source='ingredient_id.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ['__all__']


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
        return (request and request.user.is_authenticated
                and obj.favorites.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.shopping_cart.filter(user=request.user).exists())


class RecipeReadSerializerForSubscriptions(RecipeReadSerializer):

    class Meta(RecipeReadSerializer.Meta):
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']

        def validate(self, data):
            request = self.context.get('request')
            recipe = self.context.get('recipe')

            if request.method == 'POST' and Favorites.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError('Рецепт уже в избранном')

            if request.method == 'DELETE' and not Favorites.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError('Рецепт не в избранном')
            return data


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = RecipeIngredientsWriteSerializer(many=True,
                                                   required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True, required=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time']
        read_only_fields = ('author', )

    def validate(self, data):
        if 'tags' not in data:
            raise ValidationError('Поле тегов обязательно!')
        if data['tags'] == []:
            raise ValidationError('Теги не должны быть пустыми')
        if len(data['tags']) != len(set(data['tags'])):
            raise ValidationError('Теги не должны содержать дубликатов')
        if 'ingredients' not in data:
            raise serializers.ValidationError('Поле ингредиентов обязательно!')
        if data['ingredients'] == []:
            raise ValidationError("Нужно добавить ингредиенты")
        ingredient_ids = []
        for ingredient in data['ingredients']:
            ingredient_ids.append(
                ingredient.get('ingredient_id', {}).get('id'))
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Найдены дубликаты ингредиенты')
        return data

    def to_representation(self, instance):
        """Преобразуем IDs в объекты при выводе."""
        return RecipeReadSerializer(instance, context=self.context).data

    def create_update_ingredients(self, recipe, ingredients_data):
        return [RecipeIngredients(recipe_id=recipe,
                                  ingredient_id=item['id'],
                                  amount=item['amount'])
                for item in ingredients_data]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        RecipeIngredients.objects.bulk_create(
            self.create_update_ingredients(recipe, ingredients_data))
        return recipe

    def update(self, instance, validated_data):
        # instance = super().update(instance, validated_data)
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()

        if 'tags' in validated_data:
            instance.tags.set(tags_data)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            instance.recipe_ingredients.all().delete()
            RecipeIngredients.objects.bulk_create(
                self.create_update_ingredients(instance, ingredients_data))
        return instance


def get_recipes_for_user_with_limit(obj, recipes_limit):
    """Cписок рецептов автора."""
    all_recipes = obj.recipes.all()
    try:
        if recipes_limit is not None:
            recipes_to_show = all_recipes[:int(recipes_limit)]
        else:
            recipes_to_show = all_recipes
    except (ValueError):
        recipes_to_show = all_recipes

    return RecipeReadSerializerForSubscriptions(recipes_to_show,
                                                many=True).data


class SubscriptionSerializer(UserGetSerializer):
    """Сериализатор для работы с подписками на пользователей."""

    recipes = serializers.SerializerMethodField()

    class Meta(UserGetSerializer.Meta):
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'avatar']

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        return get_recipes_for_user_with_limit(obj, recipes_limit)


class UserGetSerializerFollow(SubscriptionSerializer):
    """Сериализатор для получения пользователя для подписок."""
    recipes_count = serializers.SerializerMethodField()

    class Meta(SubscriptionSerializer.Meta):
        fields = SubscriptionSerializer.Meta.fields + ['recipes',
                                                       'recipes_count']

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        return get_recipes_for_user_with_limit(obj, recipes_limit)


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


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=['user', 'recipe'],
                message={'deatail': 'Рецепт уже в избранном'}
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже в корзине!'
            )
        ]


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['user', 'following']
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message='Пользователь уже в подписках!'
            )
        ]
