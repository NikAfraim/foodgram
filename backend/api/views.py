from django.shortcuts import render, get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets, status

from recipes.models import Recipe, Tag, Ingredient, Favourites, ShopList
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from user.models import User, Subscription
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          UserCreateSerializer, UserReadSerializer,
                          SubscriptionSerializer, ShortRecipeSerializer)
from .permissions import ReadOnly, IsAdminOrReadOnly, IsAuthorOrReadOnly
from rest_framework.views import APIView
from djoser.views import UserViewSet as DjoserUserViewSet


class UserViewSet(DjoserUserViewSet):
    """View-класс реализующий операции модели User"""

    queryset = User.objects.all()
    serializer_class = UserReadSerializer

    # def get_queryset(self):
    #     return User.objects.all()

    # @action(methods=('get',), detail=False)
    # def subscriptions(self, request):
    #     if self.request.user.is_anonymous:
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)
    #
    #     # pages = self.paginate_queryset(
    #     #     User.objects.filter(subscription__user=self.request.user)
    #     # )
    #     serializer = SubscriptionSerializer(many=True)
    #     return serializer.data

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthorOrReadOnly,))
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(self.queryset, id=id)
        serializer = SubscriptionSerializer(author)
        if request.method == 'POST':
            if Subscription.objects.filter(
                    user=request.user, author=author).exists():
                raise ValidationError('Вы уже подписаны на автора')
            if user == author:
                raise ValidationError('Нельзя подписываться на самого себя!')
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            in_subscribed = Subscription.objects.filter(
                user=request.user, author=author).exists()
            if in_subscribed is False:
                raise ValidationError("Вы не были подписаны на автора!")
        Subscription.objects.filter(user=request.user, author=author).delete()
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


class SubscriptionViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Subscription"""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permissions = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        users_id = self.kwargs.get('users_id')
        serializer.save(author=users_id, user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """View-класс реализующий операции модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions = [ReadOnly]
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """View-класс реализующий операции модели Ingredient"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permissions = [ReadOnly]
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Recipe"""

    queryset = Recipe.objects.all()
    permissions = [IsAuthorOrReadOnly]

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
        user = self.request.user
        recipe = get_object_or_404(self.queryset, id=kwargs['pk'])
        serializer = ShortRecipeSerializer(recipe)
        if request.method == 'POST':
            if Favourites.objects.filter(
                    user=request.user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в избранном')
            Favourites.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            in_favorites = Favourites.objects.filter(
                user=request.user, recipe=recipe).exists()
            if in_favorites is False:
                raise ValidationError("Рецепт не в избранном")
        Favourites.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthorOrReadOnly,))
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(self.queryset, id=kwargs['pk'])
        serializer = ShortRecipeSerializer(recipe)
        if request.method == 'POST':
            if ShopList.objects.filter(
                    user=request.user, recipe=recipe).exists():
                raise ValidationError('Продукты уже в корзине')
            ShopList.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            in_shopping_cart = ShopList.objects.filter(
                user=request.user, recipe=recipe).exists()
            if in_shopping_cart is False:
                raise ValidationError("Продукты удаленны из корзины")
        ShopList.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
















