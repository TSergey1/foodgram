from django.contrib.auth import get_user_model
from djoser import views

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          FollowSerializer,
                          RecipeGetSerializer,
                          RecipeSetSerializer,
                          TagSerializer,
                          UserSerializer)
from recipes.models import (Ingredient,
                            Recipe,
                            Tag)
from users.models import Follow


User = get_user_model()


class UserViewSet(views.UserViewSet):
    """Вьюсет для обьектов класса User."""

    def get_permissions(self):
        """
        Переопределяем get_permissions для доступа только авторизованным пользователям
        к эндпоинту users/me/.
        """
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=True,
            url_path='subscriptions',
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """
        Реализация для доступа только авторизованным пользователям
        к эндпоинту users/subscriptions/
        """
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """
        Реализация для доступа только авторизованным пользователям
        к эндпоинту users/{id}/subscribe/
        """
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet подписки"""
    queryset = User.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов класса Recipe."""

    queryset = Recipe.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tags__slug',)
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Автоматически записываем автора."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSetSerializer
