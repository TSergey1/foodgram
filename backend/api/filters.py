from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilters(filters.FilterSet):
    """Класс фильтров полей модели Title"""

    tags = filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
