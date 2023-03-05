from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models

from user.models import User

MIN_VALUE_FOR_AMOUNT = 1
MIN_VALUE_FOR_COOKING_TIME = 1

ORANGE = '#E26C2D'
GREEN = '#49B64E'
PURPLE = '#8775D2'
BLUE = '#4A61DD'
YELLOW = '#F9A62B'


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.LIMIT_CHAR_200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.LIMIT_CHAR_200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        default_related_name = 'Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов"""
    COLOR = (
        (ORANGE, 'Оранжевый'),
        (GREEN, 'Зеленый'),
        (PURPLE, 'Фиолетовый')
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.LIMIT_CHAR_200,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=settings.LIMIT_CHAR_7,
        choices=COLOR
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.LIMIT_CHAR_200
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.LIMIT_CHAR_200,
        help_text='Напишите название блюда'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        help_text='Прикрепите картинку с блюдом'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание для блюда'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Введите данные об ингредиентах'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(MIN_VALUE_FOR_COOKING_TIME)
        ]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name[:20]}'


class IngredientAmount(models.Model):
    """Модель ингредиентов с количеством"""
    recipes = models.ForeignKey(
        Recipe,
        verbose_name='Название блюда',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиенты',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_VALUE_FOR_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class AbstractModel(models.Model):
    """Абстрактная модель для Favourite и ShopList"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Список покупок',
    )

    class Meta:
        abstract = True,

    def __str__(self):
        return f'{self.recipe}'


class Favourites(AbstractModel):
    """Модель избранного"""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favourites'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favourite',
            )
        ]


class ShopList(AbstractModel):
    """Модель списка покупок"""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'shop_list'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shop_list',
            )
        ]
