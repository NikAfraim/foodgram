from django.contrib import admin

from .models import Recipe, Tag, Ingredient, IngredientAmount, Favourites, \
    ShopList

admin.site.site_header = 'Admin foodgram'
admin.site.site_title = 'Admin foodgram'


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'image', 'text', 'cooking_time')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    inlines = [IngredientInline, ]
    list_editable = ('text', 'image', 'name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_editable = ('name', 'color', 'slug')


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




