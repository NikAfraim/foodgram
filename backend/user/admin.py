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
    )
    list_filter = ('username', 'email')
    search_fields = ('username',)
    list_editable = ('username',)

    def full_name(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)
    full_name.short_description = 'Полное имя'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка Subscription для панели Admin"""

    list_display = ('pk', 'author', 'user',)
    list_filter = ('user',)
    search_fields = ('user',)
