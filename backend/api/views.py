from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipesFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavouritesSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShopListSerializer, SubscriptionSerializer,
                          TagSerializer, UserReadSerializer)

from recipes.models import (Favourites, Ingredient, IngredientAmount, Recipe,
                            ShopList, Tag)
from user.models import Subscription, User


class UserViewSet(DjoserUserViewSet):
    """View-класс реализующий операции модели User"""

    queryset = User.objects.all()
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
        get_object_or_404(Subscription, user=request.user,
                          author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            pagination_class=CustomPagination)
    def subscriptions(self, request):
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        pages = self.paginate_queryset(
            User.objects.filter(author__user=self.request.user)
        )
        serializer = SubscriptionSerializer(pages, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Mixins классов Tag и Ingredients."""
    pagination_class = None
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
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
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name',)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            methods=['post'],
            permission_classes=(IsAuthorOrReadOnly,))
    def favorite(self, request, **kwargs):
        return self.create_obj(kwargs['pk'], request,
                               FavouritesSerializer)

    @favorite.mapping.delete
    def delete_favourite(self, request, **kwargs):
        return self.delete_obj(kwargs['pk'], request,
                               Favourites)

    @action(detail=True,
            methods=['post'],
            permission_classes=(IsAuthorOrReadOnly,))
    def shopping_cart(self, request, **kwargs):
        return self.create_obj(kwargs['pk'], request,
                               ShopListSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        return self.delete_obj(kwargs['pk'], request,
                               ShopList)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthorOrReadOnly,))
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientAmount.objects
            .filter(recipes__shop_list__user=request.user)
            .order_by('ingredient__name').values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name', 'total_amount',
                'ingredient__measurement_unit'
            )
        )
        return self.download(ingredients)

    @staticmethod
    def create_obj(recipe_id, request, serializer):
        data = {'user': request.user.id, 'recipe': recipe_id}
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_obj(recipe_id, request, model):
        get_object_or_404(model, user=request.user,
                          recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def download(obj):
        file_list = []
        [file_list.append('{} - {} {}.'.format(*value))
         for value in obj]
        file = HttpResponse('Список покупок: \n\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = 'attachment; filename=shopping_list'
        return file
