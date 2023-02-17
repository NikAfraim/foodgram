from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка User для панели Admin"""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('username',)
    search_fields = ('username',)
    list_editable = ('first_name', 'last_name', 'username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = ('pk', 'author', 'user',)
    list_filter = ('user',)
    search_fields = ('user',)
