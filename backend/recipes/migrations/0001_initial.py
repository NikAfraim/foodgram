# Generated by Django 2.2.16 on 2023-02-17 20:21

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': ('Ингридиент',),
                'verbose_name_plural': 'Ингридиенты',
                'default_related_name': 'Ingredients',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('name', models.CharField(help_text='Напишите название блюда', max_length=200, verbose_name='Название')),
                ('image', models.ImageField(help_text='Прикрепите картинку с блюдом', upload_to='recipes/', verbose_name='Картинка')),
                ('text', models.TextField(help_text='Описание для блюда', max_length=200, verbose_name='Описание')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время готовки')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredients', models.ManyToManyField(help_text='Введите данные об ингредиентах', related_name='recipes', to='recipes.Ingredient', verbose_name='Ингредиенты')),
            ],
            options={
                'verbose_name': ('Рецепт',),
                'verbose_name_plural': ('Рецепты',),
                'ordering': ('-pub_date',),
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('breakfast', 'Завтрак'), ('lunch', 'обед'), ('dinner', 'ужин')], max_length=200, verbose_name='Название')),
                ('color', models.CharField(choices=[('#E26C2D', 'Оранжевый'), ('#49B64E', 'Зеленый'), ('#8775D2', 'Фиолетовый'), ('#4A61DD', 'Синий'), ('#F9A62B', 'Желтый')], max_length=7, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': ('Тег',),
                'verbose_name_plural': ('Теги',),
                'default_related_name': 'tags',
            },
        ),
        migrations.CreateModel(
            name='ShopList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_list', to='recipes.Recipe', verbose_name='Список покупок')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_list', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': ('Список покупок',),
                'verbose_name_plural': ('Список покупок',),
                'default_related_name': 'shop_list',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите теги', related_name='recipes', to='recipes.Tag', verbose_name='Теги'),
        ),
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_amount', to='recipes.Ingredient', verbose_name='Ингридиенты')),
                ('recipes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes_amount', to='recipes.Recipe', verbose_name='Название блюда')),
            ],
            options={
                'verbose_name': ('Количество ингредиентов',),
                'verbose_name_plural': ('Количество ингредиентов',),
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='Favourites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to='recipes.Recipe', verbose_name='Название рецепта')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': ('Избранное',),
                'verbose_name_plural': ('Избранное',),
            },
        ),
    ]
