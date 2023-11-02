from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          FollowSerializer,
                          RecipeGetSerializer,
                          RecipeSetSerializer,
                          RecipesShortSerializer,
                          TagSerializer,)
from recipes.models import (BuyRecipe,
                            Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            Tag)
from users.models import Follow


User = get_user_model()


class UserViewSet(views.UserViewSet):
    """Вьюсет для обьектов класса User."""

    def get_permissions(self):
        """
        Переопределяем get_permissions для доступа только авторизованным
        пользователям к эндпоинту users/me/.
        """
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=False,
            url_path='subscriptions',
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Реализация эндпоинта users/subscriptions/ю"""
        user = request.user
        folowing = User.objects.filter(following__user=user)
        serializer = FollowSerializer(folowing, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        """
        Реализация эндпоинта users/{id}/subscribe/
        """
        user = request.user
        following = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = FollowSerializer(following,
                                          context={'request': request})
            if user == following:
                return Response({'errors': 'Нельзя подписаться на себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, following=following).exists():
                return Response({'errors': 'Вы уже подписаны на автора!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status.HTTP_201_CREATED)
        follower = Follow.objects.filter(user=user, following=following)
        if follower.exists():
            follower.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы не подписаны на автора!'},
                        status=status.HTTP_400_BAD_REQUEST)


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

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='favorite',
            serializer_class=RecipesShortSerializer,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """
        Реализация эндпоинта recipe/{id}/favorite/
        """
        user = request.user
        in_favorites = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = RecipesShortSerializer(in_favorites,
                                                context={'request': request})
            if FavoriteRecipe.objects.filter(user=user,
                                             recipe=in_favorites).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранных!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=in_favorites)
            return Response(serializer.data, status.HTTP_201_CREATED)
        favorites = FavoriteRecipe.objects.filter(user=user,
                                                  recipe=in_favorites)
        if favorites.exists():
            favorites.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Этот рецепт не в избранных!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='shopping_cart',
            serializer_class=RecipesShortSerializer,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """
        Реализация эндпоинта recipe/{id}/shopping_cart/
        """
        user = request.user
        object_to_add = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = RecipesShortSerializer(object_to_add,
                                                context={'request': request})
            if BuyRecipe.objects.filter(user=user,
                                        recipe=object_to_add).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            BuyRecipe.objects.create(user=user, recipe=object_to_add)
            return Response(serializer.data, status.HTTP_201_CREATED)
        object_to_delete = BuyRecipe.objects.filter(user=user,
                                                    recipe=object_to_add)
        if object_to_delete.exists():
            object_to_delete.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Этот рецепт не в списке покупок!'},
                        status=status.HTTP_400_BAD_REQUEST)
