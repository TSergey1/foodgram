from django.contrib.auth import get_user_model
from djoser import views

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (IngredientSerializer,
                          ReadRecipeSerializer,
                          RecipeSerializer,
                          SubscriptionSerializer,
                          TagSerializer)
from recipes.models import (Ingredient,
                            Recipe,
                            Tag)

User = get_user_model()


class UserViewSet(views.UserViewSet):
    """Вьюсет для обьектов класса User."""

    @action(methods=['get', 'post', 'delete'],
            detail=True,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,),
            serializer_class=SubscriptionSerializer)
    def subscribe(self, request):
        user = request.user
        if request.method == 'POST':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        if request.method == 'DELETE':
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов класса Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return RecipeSerializer
