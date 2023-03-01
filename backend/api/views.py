from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from recipes.models import (Favourites, Ingredient, IngredientAmount, Recipe,
                            ShopList, Tag)
from user.models import Subscription, User

from .filters import IngredientFilter, RecipesFilter
from .permissions import IsAuthor, IsAuthorOrReadOnly, ReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShortRecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserReadSerializer, FavouritesSerializer,
                          ShopListSerializer, UserCreateSerializer)


class UserViewSet(DjoserUserViewSet):
    """View-класс реализующий операции модели User"""

    queryset = User.objects.all()

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #         return UserReadSerializer
    #     return UserCreateSerializer
    serializer_class = UserReadSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthorOrReadOnly,))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionSerializer(author, data=request.data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Subscription.objects.filter(user=request.user,
                                        author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        pages = self.paginate_queryset(
            User.objects.filter(author__user=self.request.user)
        )
        serializer = SubscriptionSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Mixins классов Tag и Ingredients."""
    pagination_class = None
    filter_backends = (filters.SearchFilter,  DjangoFilterBackend,)
    search_fields = ('name',)


class TagViewSet(ListRetrieveViewSet):
    """View-класс реализующий операции модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    """View-класс реализующий операции модели Ingredient"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Recipe"""

    queryset = Recipe.objects.all()
    permissions = [IsAuthorOrReadOnly]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name',)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthorOrReadOnly,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(self.queryset, id=kwargs['pk'])
        serializer = FavouritesSerializer(recipe, data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Favourites.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Favourites.objects.filter(user=request.user,
                                      recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthor,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(self.queryset, id=kwargs['pk'])
        serializer = ShopListSerializer(recipe, data=request.data,
                                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            ShopList.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShopList.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthor,))
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientAmount.objects
            .filter(recipes__shop_list__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__measurement_unit'
            )
        )
        filename = 'shopping_list.txt'
        file_list = []
        [file_list.append('{} - {} {}.'.format(*ingredient))
         for ingredient in ingredients]
        file = HttpResponse('Список покупок: \n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = f'attachment; filename={filename}'
        return file
