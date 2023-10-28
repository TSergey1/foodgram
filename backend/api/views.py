from django.contrib.auth import get_user_model

from rest_framework import viewsets

from .serializers import (IngredientSerializer,
                          TagSerializer)
from recipes.models import (Ingredient,
                            Tag)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
