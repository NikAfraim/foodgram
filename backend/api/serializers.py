import base64
from collections import OrderedDict

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favourites, Ingredient, IngredientAmount, Recipe,
                            ShopList, Tag)
from user.models import Subscription, User


class UserCreateSerializer(UserCreateSerializer):
    """Преобразование данных класса User на создание"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )


class UserReadSerializer(UserSerializer):
    """Преобразование данных класса User на чтение"""
    is_subscribed = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            author=obj, user=request.user
        ).exists()


class Base64ImageField(serializers.ImageField):
    """Преобразование данных поля Image"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super(Base64ImageField, self).to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Преобразование данных класса Recipe в короткой форме для
    Subscription, Favourite, ShopList
    """

    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(UserReadSerializer):
    """Преобразование данных класса User для подписки"""
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def validate(self, data):
        request = self.context['request']
        author = self.instance

        if request.method == 'POST':
            if Subscription.objects.filter(
                    user=request.user,
                    author=author).exists():
                raise ValidationError(
                    'Вы уже подписаны на автора')
            if request.user == author:
                raise ValidationError(
                    'Нельзя подписываться на самого себя!')
        if request.method == 'DELETE':
            if not  Subscription.objects.filter(
                    user=request.user, author=author
            ).exists():
                raise ValidationError(
                    "Вы не были подписаны на автора!")
        return data

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Tag"""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Ingredient"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Преобразование данных класса IngredientAmount"""
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Recipe на запись"""
    ingredients = IngredientAmountSerializer(
        many=True
    )
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='id',
        many=True
    )
    image = Base64ImageField(required=True)
    author = UserReadSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['id'] = instance.id

        representation['ingredients'] = IngredientAmountSerializer(
            IngredientAmount.objects.filter(recipes=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        representation = OrderedDict([
            ('id', representation['id']),
            ('tags', representation['tags']),
            ('author', representation['author']),
            ('ingredients', representation['ingredients']),
            ('is_favorited', representation['is_favorited']),
            ('is_in_shopping_cart', representation['is_in_shopping_cart']),
            ('image', representation['image']),
            ('name', representation['name']),
            ('text', representation['text']),
            ('cooking_time', representation['cooking_time']),
        ])
        return representation

    @staticmethod
    def recipes_ingredients_add(ingredients, recipe):
        for ingredient in ingredients:
            current_ingredient = (
                Ingredient.objects.get(id=ingredient['id'])
            )
            IngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipes=recipe,
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        self.recipes_ingredients_add(ingredients, recipes)
        return recipes

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipes=instance).delete()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        self.recipes_ingredients_add(ingredients, instance)
        return super().update(instance, validated_data)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        requests = self.context.get('request')
        if not requests or requests.user.is_anonymous:
            return False
        return ShopList.objects.filter(
            recipe=obj, user=requests.user
        ).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Recipe на чтение"""
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id

        representation['ingredients'] = IngredientAmountSerializer(
            IngredientAmount.objects.filter(recipes=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        representation = OrderedDict([
            ('id', representation['id']),
            ('tags', representation['tags']),
            ('author', representation['author']),
            ('ingredients', representation['ingredients']),
            ('is_favorited', representation['is_favorited']),
            ('is_in_shopping_cart', representation['is_in_shopping_cart']),
            ('image', representation['image']),
            ('name', representation['name']),
            ('text', representation['text']),
            ('cooking_time', representation['cooking_time']),
        ])
        return representation

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        requests = self.context.get('request')
        if not requests or requests.user.is_anonymous:
            return False
        return ShopList.objects.filter(
            recipe=obj, user=requests.user
        ).exists()


class FavouritesSerializer(ShortRecipeSerializer):
    """Преобразование данных класса Favourite"""

    def validate(self, data):
        request = self.context['request']
        recipe = self.instance

        if request.method == 'POST':
            if Favourites.objects.filter(
                    user=request.user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в избранном')
        if request.method == 'DELETE':
            if not Favourites.objects.filter(
                    user=request.user, recipe=recipe
            ).exists():
                raise ValidationError("Рецепт не в избранном")
        return data


class ShopListSerializer(ShortRecipeSerializer):
    """Преобразование данных класса ShopList"""

    def validate(self, data):
        requests = self.context['request']
        recipe = self.instance

        if requests.method == 'POST':
            if ShopList.objects.filter(
                    user=requests.user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в списке покупок')
        if requests.method == "DELETE":
            if not ShopList.objects.filter(
                    user=requests.user, recipe=recipe
            ).exists():
                raise ValidationError('Рецепта нету в списке покупок')
        return data
