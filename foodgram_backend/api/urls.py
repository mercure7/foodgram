from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewset, IngredientViewset,
                    CustomUserViewset, redirect_short_link)

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewset, basename='tags')
router.register('ingredients', IngredientViewset, basename='ingredients')
router.register('users', CustomUserViewset, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('s/<slug:code>/', redirect_short_link, name='short_link_redirect'),
    path('', include(router.urls))
]
