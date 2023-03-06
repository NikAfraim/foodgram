from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import Sum

from .models import (Favourites, Ingredient, IngredientAmount, Recipe,
                     ShopList, Tag)

admin.site.unregister(Group)

admin.site.site_header = 'Админ-зона foodgram'
admin.site.site_title = 'Админ-зона foodgram'


class IngredientInline(admin.TabularInline):
    """Настройка IngredientAmount для панели Admin"""

    model = IngredientAmount
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка Recipe для панели Admin"""
    list_display = ('pk', 'author', 'name',
                    'recipe_ingredients', 'cooking_time', 'count')
    filter_horizontal = ('tags',)
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'name', 'tags')
    inlines = [IngredientInline, ]
    list_editable = ('name',)

    def count(self, obj):
        return Favourites.objects.filter(recipe=obj).count()
    count.short_description = 'Количество подписок'

    def recipe_ingredients(self, obj):
        ingredients = (
            IngredientAmount.objects
            .filter(recipes=obj)
            .order_by('ingredient__name').values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name', 'total_amount',
                'ingredient__measurement_unit'
            )
        )
        ingredient_list = []
        [ingredient_list.append('{} - {} {}.'.format(*ingredient))
         for ingredient in ingredients]
        return ingredient_list
    recipe_ingredients.short_description = 'Ингредиенты'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка Tag для панели Admin"""

    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_editable = ('name', 'color', 'slug')
