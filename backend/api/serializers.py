from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import (Favourites, Ingredient, IngredientAmount, Recipe,
                            ShopList, Tag)
from user.models import Subscription, User

MIN_VALUE_FOR_AMOUNT = 1
MIN_VALUE_FOR_COOKING_TIME = 1


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
        return (
            request and request.user.is_authenticated
            and Subscription.objects.filter(
                author=obj, user=request.user
            ).exists()
        )


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
    recipes = serializers.SerializerMethodField()
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
                raise serializers.ValidationError(
                    'Вы уже подписаны на автора')
            if request.user == author:
                raise serializers.ValidationError(
                    'Нельзя подписываться на самого себя!')
        if request.method == 'DELETE':
            if not Subscription.objects.filter(
                    user=request.user, author=author
            ).exists():
                raise serializers.ValidationError(
                    "Вы не были подписаны на автора!")
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj).all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True,
                                           context={'request': request})
        return serializer.data

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
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Recipe на запись"""
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredientamount_set'
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
    cooking_time = serializers.IntegerField()

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

    def validate(self, attrs):
        tags = []
        for tag in attrs['tags']:
            if tag not in tags:
                tags.append(tag)
            else:
                raise serializers.ValidationError(
                    {'tags': 'Тег должен быть уникальным'}
                )
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Должен быть выбран хотя бы один тег'}
            )
        ingredients = []
        for ingredient in attrs['ingredientamount_set']:
            if ingredient['ingredient'] not in ingredients:
                ingredients.append(ingredient['ingredient'])
            else:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиент должен быть уникальным'}
                )
            if int(ingredient['amount']) < MIN_VALUE_FOR_AMOUNT:
                raise serializers.ValidationError(
                    {'amount': 'Минимальный объем|вес 1'}
                )
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Должен быть выбран хотя бы один ингредиент'}
            )
        if int(attrs['cooking_time']) < MIN_VALUE_FOR_COOKING_TIME:
            raise serializers.ValidationError(
                {'cooking_time': 'Минимальное время приготовления 1'}
            )
        return attrs

    @staticmethod
    def recipes_ingredients_add(ingredients, recipe):
        ingredients_amount = [
            IngredientAmount(
                ingredient=Ingredient.objects.get(
                    id=ingredient['ingredient']['id']
                ),
                recipes=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientAmount.objects.bulk_create(ingredients_amount)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientamount_set')
        recipes = Recipe.objects.create(**validated_data,
                                        author=self.context['request'].user)
        recipes.tags.set(tags)
        self.recipes_ingredients_add(ingredients, recipes)
        return recipes

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipes=instance).delete()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredientamount_set')
        self.recipes_ingredients_add(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Recipe на чтение"""
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredientamount_set'
    )
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and Favourites.objects.filter(
                recipe=obj, user=request.user
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and ShopList.objects.filter(
                recipe=obj, user=request.user
            ).exists()
        )


class FavouritesSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Favourite"""

    def validate(self, data):
        request = self.context['request']

        if request.method == 'POST':
            if Favourites.objects.filter(
                    user=data['user'], recipe=data['recipe']).exists():
                raise serializers.ValidationError('Рецепт уже в избранном')
        if request.method == 'DELETE':
            if not Favourites.objects.filter(
                    user=data['user'], recipe=data['recipe']
            ).exists():
                raise serializers.ValidationError("Рецепт не в избранном")
        return data

    class Meta:
        model = Favourites
        fields = (
            'user',
            'recipe'
        )


class ShopListSerializer(serializers.ModelSerializer):
    """Преобразование данных класса ShopList"""

    def validate(self, data):
        requests = self.context['request']

        if requests.method == 'POST':
            if ShopList.objects.filter(
                    user=data['user'], recipe=data['recipe']).exists():
                raise serializers.ValidationError(
                    'Рецепт уже в списке покупок')
        if requests.method == "DELETE":
            if not ShopList.objects.filter(
                    user=data['user'], recipe=data['recipe']
            ).exists():
                raise serializers.ValidationError(
                    'Рецепта нету в списке покупок')
        return data

    class Meta:
        model = ShopList
        fields = (
            'user',
            'recipe'
        )
