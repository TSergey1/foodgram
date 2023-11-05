import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from recipes.models import Ingredient

ROOT_DATA = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """Импорт данных из json файлов
    BASE_DIR / data."""

    help = 'loading ingredients from data in json'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.json', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(ROOT_DATA, options['filename']), 'r') as f:
                data = json.load(f)
                for i in data:
                    try:
                        Ingredient.objects.create(
                            name=i['name'],
                            measurement_unit=i['measurement_unit']                
                        )
                    except IntegrityError:
                        print(
                            f'Ингридиет {i["name"]} '
                            f'{i["measurement_unit"]} '
                            f'уже есть в базе'
                        )
        except FileNotFoundError:
            raise CommandError('Файл data отсутствует')
