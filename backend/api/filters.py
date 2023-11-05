from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

# from recipes.models import Recipe

User = get_user_model()


class RecipeFilters(filters.FilterSet):

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(buy_recipe__user=self.request.user)
        return queryset
