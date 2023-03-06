import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag

PATH_CSV_INGREDIENTS = './data/ingredients.csv'
PATH_CSV_TAGS = './data/tags.csv'


class Command(BaseCommand):
    help = 'Загрузка csv в ДТ'

    def handle(self, *args, **options):
        with open(PATH_CSV_INGREDIENTS, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for name, measurement_unit in reader:
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
        with open(PATH_CSV_TAGS, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for name, color, slug in reader:
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
        self.stdout.write('Данные из списка ингредиентов и тегов загружены')
