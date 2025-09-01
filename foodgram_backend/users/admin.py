from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('first_name', 'last_name', 'email')
    empty_value_display = 'Значение не задано'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
