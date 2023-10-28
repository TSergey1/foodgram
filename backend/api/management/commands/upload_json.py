from django.core.management.base import BaseCommand
import json
from recipes.models import Ingredient


class Command(BaseCommand):
    """Импорт данных из json файлов
    BASE_DIR / data."""
    def handle(self, *args, **options):

        with open('data.ingredient.json', 'rb') as f:
            data = json.load(f)

            for i in data:
                ingredient = Ingredient()
                ingredient.name = i['name']
                ingredient.measurement_unit = i['measurement_unit']
                ingredient.save()

# from django.core.management.base import (BaseCommand,
#                                          CommandError)
# from django.shortcuts import get_object_or_404
# from django.apps import apps
# from foodgram import settings
# import csv

# DATA_DIR = settings.BASE_DIR / 'static' / 'data'
# FOREIGNKEY_FIELDS = ('category', 'author', 'genre', 'title', 'review')
# CSV_NAMES = [
#     'users.csv',
#     'category.csv',
#     'genre.csv',
#     'titles.csv',
#     'genre_title.csv',
#     'review.csv',
#     'comments.csv',
# ]


# class Command(BaseCommand):
#     help = """Импорт данных из csv файлов
#     (BASE_DIR / static / data)."""

#     def get_csv_file(self, filename):
#         """Путь к csv файлу."""
#         file_path = settings.BASE_DIR / 'static' / 'data' / filename
#         return file_path

#     def get_name_model(self, file_name):
#         """Имя модели по имени csv файла."""
#         name_model = file_name.rstrip('.csv')
#         if '_' in name_model:
#             name_model = name_model.replace('_', '')
#         return name_model

#     def get_model(self, model_name):
#         """Имя модели по полю из csv файла."""
#         if model_name == 'author':
#             Model = apps.get_model('reviews', 'user')
#         else:
#             Model = apps.get_model('reviews', model_name)
#         if not Model:
#             raise CommandError(f'Модели {Model} не существует')
#         return Model

#     def load_csv(self, csv_name):
#         model_name = self.get_name_model(csv_name)
#         file_path = self.get_csv_file(csv_name)
#         Model = self.get_model(model_name)
#         try:
#             with open(file_path) as file:
#                 self.stdout.write(f'Чтение файла {csv_name}')
#                 reader = csv.DictReader(file)
#                 for row in reader:
#                     Obj = Model()
#                     for i, field in enumerate(row.values()):
#                         if reader.fieldnames[i] in FOREIGNKEY_FIELDS:
#                             model = self.get_model(reader.fieldnames[i])
#                             obj = get_object_or_404(model, id=field)
#                             setattr(Obj, reader.fieldnames[i], obj)
#                         else:
#                             setattr(Obj, reader.fieldnames[i], field)
#                     Obj.save()
#         except Exception as e:
#             raise CommandError(
#                 f'При чтении файла {csv_name} произошла ошибка: {e}'
#             )
#         else:
#             self.stdout.write(
#                 self.style.SUCCESS(
#                     f'Данные из файла {csv_name} успешно занесены в БД'
#                 )
#             )

#     def handle(self, *args, **options):
#         for csv_name in CSV_NAMES:
#             self.load_csv(csv_name)
