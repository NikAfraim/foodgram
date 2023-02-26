from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Поиск ингредиента по полю name регистронезависимо
        начиная с указанного значения"""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    """Фильтрация по:
        тегам, в избранном, в списке покупок"""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags',
        label='slug',
    )
    is_favourited = filters.BooleanFilter(
        method='get_favourite',
        label='favourite',
    )
    is_in_shopping_list = filters.BooleanFilter(
        method='get_is_in_shopping_list',
        label='shopping_list',
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favourited',
            'is_in_shopping_list',
        )

    def get_favourite(self, queryset, name, value):

        if value:

            return queryset.filter(is_faourited__user=self.request.user)

        return queryset.exclude(is_favourited=self.request.user)

    def get_is_in_shopping_list(self, queryset, name, value):

        if value:

            return Recipe.objects.filter(
                is_in_shopping_list__user=self.request.user
            )

        return Recipe.objects.all()
