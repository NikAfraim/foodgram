from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка User для панели Admin"""

    list_display = (
        'pk',
        'full_name',
        'username',
        'email',
        'count_sub',
        'count_recipe'
    )
    list_filter = ('username', 'email')
    search_fields = ('username',)
    list_editable = ('username',)

    def full_name(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)
    full_name.short_description = 'Полное имя'

    def count_sub(self, obj):
        return obj.author.count()
    count_sub.short_description = 'Количество подписчиков'

    def count_recipe(self, obj):
        return obj.recipes.count()
    count_recipe.short_description = 'Количество рецептов'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка Subscription для панели Admin"""

    list_display = ('pk', 'author', 'user',)
    list_filter = ('user',)
    search_fields = ('user',)
