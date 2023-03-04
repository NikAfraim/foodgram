# Generated by Django 4.1.7 on 2023-03-04 22:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_alter_favourites_id_alter_ingredient_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favourites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Список покупок'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время готовки'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(help_text='Описание для блюда', verbose_name='Описание'),
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('name', 'measurement_unit')},
        ),
        migrations.AddConstraint(
            model_name='favourites',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_favourite'),
        ),
        migrations.AddConstraint(
            model_name='shoplist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shop_list'),
        ),
    ]