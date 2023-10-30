from django.contrib.auth import get_user_model
from djoser import views

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          UserSerializer)
from recipes.models import (Ingredient,
                            Recipe,
                            Tag)

User = get_user_model()


class UserViewSet(views.UserViewSet):
    """Вьюсет для обьектов класса User."""

    @action(detail=False,
            url_path='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UserSerializer)
    def me(self, request):
        """Реализация для доступа только авторизованным пользователям."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


# class FollowViewSet(mixins.CreateModelMixin,
#                     mixins.ListModelMixin,
#                     viewsets.GenericViewSet):
#     """ViewSet подписки"""
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('following__username',)

#     def get_queryset(self):
#         return self.request.user.follower

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов класса Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        """Создание отзыва, с проверкой на уникальнось в сериализаторе."""
        serializer.save(author=self.request.user)

    # def get_serializer_class(self):
    #     if self.action in ('list', 'retrieve'):
    #         return ReadRecipeSerializer
    #     return RecipeSerializer
