import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers


from recipes.models import Recipes, Ingredients, Tags, RecipeIngredients

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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
    # author = UserSerializer(read_only=True)
    image = Base64ImageField()
    author = User.objects.get(id=1)

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'image', 'cooking_time']
