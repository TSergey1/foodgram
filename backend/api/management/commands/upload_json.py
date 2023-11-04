from django.core.management.base import BaseCommand
import json
from recipes.models import Ingredient


class Command(BaseCommand):
    """Импорт данных из json файлов
    BASE_DIR / data."""
    def handle(self, *args, **options):

        with open('../data/ingredient.json', 'rb') as f:
            data = json.load(f)

            for i in data:
                ingredient = Ingredient()
                ingredient.name = i['name']
                ingredient.measurement_unit = i['measurement_unit']
                ingredient.save()
