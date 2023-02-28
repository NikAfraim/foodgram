from django.contrib import admin

from .models import (Favourites, Ingredient, IngredientAmount, Recipe,
                     ShopList, Tag)

admin.site.site_header = 'Admin foodgram'
admin.site.site_title = 'Admin foodgram'


class IngredientInline(admin.TabularInline):
    """Настройка IngredientAmount для панели Admin"""

    model = IngredientAmount
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка Recipe для панели Admin"""
    list_display = ('pk', 'author', 'name', 'cooking_time', 'count')
    filter_horizontal = ('tags',)
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'name', 'tags')
    inlines = [IngredientInline, ]
    list_editable = ('name',)

    def count(self, obj):
        return Favourites.objects.filter(recipe=obj).count()
    count.short_description = 'Количество подписок'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка Tag для панели Admin"""

    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_editable = ('name', 'color', 'slug')


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    """Настройка IngredientAmount для панели Admin"""

    list_display = ('pk', 'ingredient', 'recipes', 'amount')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка Ingredient для панели Admin"""

    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    list_editable = ('name', 'measurement_unit',)


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    """Настройка Favourites для панели Admin"""

    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_editable = ('recipe',)


@admin.register(ShopList)
class ShopListAdmin(admin.ModelAdmin):
    """Настройка ShopList для панели Admin"""

    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_editable = ('recipe',)
