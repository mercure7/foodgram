from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewset, IngredientViewset

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewset, basename='tags')
router.register('ingredients', IngredientViewset, basename='ingredients')

urlpatterns = [
    path('', include(router.urls))
]
