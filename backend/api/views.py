import aspose.pdf as ap
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from recipes.models import (BuyRecipe, FavoriteRecipe,
                            Ingredient, IngredientRecipe,
                            Recipe, Tag)
from users.models import Follow

from .filters import RecipeFilters
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipeSetSerializer,
                          RecipesShortSerializer, TagSerializer)

User = get_user_model()

DICT_ERRORS = {
    'subscribe_to_myself': 'Нельзя подписаться на себя!',
    're-subscription': 'Вы уже подписаны на автора!',
    'not_subscription': 'Вы не подписаны на автора!',
    're-favorite': 'Рецепт уже в избранных!',
    'not_favorite': 'Этот рецепт не в избранных!',
    're-buy_recipe': 'Рецепт уже в списке покупок!',
    'not_buy_recipe': 'Этот рецепт не в списке покупок!',
}


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
                return Response(
                    {'errors': '{0}'.format(
                        DICT_ERRORS['subscribe_to_myself']
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, following=following).exists():
                return Response(
                    {'errors': '{0}'.format(DICT_ERRORS['re-subscription'])},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status.HTTP_201_CREATED)
        follower = Follow.objects.filter(user=user, following=following)
        if follower.exists():
            follower.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': '{0}'.format(DICT_ERRORS['re-subscription'])},
            status=status.HTTP_400_BAD_REQUEST
        )


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
    filterset_class = RecipeFilters
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        """Автоматически записываем автора."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSetSerializer

    @action(methods=['POST', 'DELETE'],
            detail=True,
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
                    {'errors': '{0}'.format(DICT_ERRORS['re-favorite'])},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=in_favorites)
            return Response(serializer.data, status.HTTP_201_CREATED)
        favorites = FavoriteRecipe.objects.filter(user=user,
                                                  recipe=in_favorites)
        if favorites.exists():
            favorites.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response({'errors': '{0}'.format(DICT_ERRORS['not_favorite'])},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """
        Реализация эндпоинта recipe/{id}/shopping_cart/
        """
        user = request.user
        add_obj = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = RecipesShortSerializer(add_obj,
                                                context={'request': request})
            if BuyRecipe.objects.filter(user=user,
                                        recipe=add_obj).exists():
                return Response(
                    {'errors': '{0}'.format(DICT_ERRORS['re-buy_recipe'])},
                    status=status.HTTP_400_BAD_REQUEST
                )
            BuyRecipe.objects.create(user=user, recipe=add_obj)
            return Response(serializer.data, status.HTTP_201_CREATED)
        object_to_delete = BuyRecipe.objects.filter(user=user,
                                                    recipe=add_obj)
        if object_to_delete.exists():
            object_to_delete.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': '{0}'.format(DICT_ERRORS['not_buy_recipe'])},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """
        Реализация скачивание списка ингридиентов
        """
        download_dict = {}
        qw_st = IngredientRecipe.objects.filter(
            recipe__buy_recipe__user=request.user
        ).values_list(
            'ingredient__name',
            'amount',
            'ingredient__measurement_unit', )
        print(qw_st)
        for name, amount, measurement_unit in qw_st:
            if name in download_dict:
                download_dict[name][0] = download_dict[name][0] + amount
            else:
                download_dict[name] = [amount, measurement_unit]

        list_ingredient = ap.Document()
        page = list_ingredient.pages.add()
        for key, value in download_dict.items():
            text_fragment = (
                ap.text.TextFragment(f'{key} {value[0]} {value[1]}')
            )
            page.paragraphs.add(text_fragment)
        list_ingredient.save('list_ingredient.pdf')
        response = HttpResponse(
            list_ingredient,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = ('attachment; '
                                           'filename="list_ingredient.pdf"')
        return response
