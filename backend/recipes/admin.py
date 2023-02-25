from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

from .models import Recipe, Tag, Ingredient, IngredientAmount, Favourites, \
    ShopList, TagRecipe

admin.site.site_header = 'Admin foodgram'
admin.site.site_title = 'Admin foodgram'


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class FavouritesInline(admin.TabularInline):
    model = Favourites


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'cooking_time', 'count')
    filter_horizontal = ('tags',)
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'name', 'tags')
    inlines = [IngredientInline, ]
    list_editable = ('name',)

    def count(self, obj):
        return Favourites.objects.filter(recipe=obj).count()
    count.short_description = 'Количество подписок'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tag', 'recipe')
    # search_fields = ('name',)
    list_editable = ('tag', 'recipe')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_editable = ('name', 'color', 'slug')


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'recipes', 'amount')
    # search_fields = ('name',))


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_editable = ('name', 'measurement_unit',)


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_editable = ('recipe',)


@admin.register(ShopList)
class ShopListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_editable = ('recipe',)




