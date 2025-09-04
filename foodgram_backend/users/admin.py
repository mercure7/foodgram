from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'subscribers',
        'recipes'
    )
    search_fields = ('first_name', 'last_name', 'email')
    empty_value_display = 'Значение не задано'

    @admin.display(empty_value="-", description='Количество рецептов')
    def recipes(self, obj):
        return obj.recipes.count()

    @admin.display(empty_value="-", description='Число подписчиков')
    def subscribers(self, obj):
        return obj.following.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
