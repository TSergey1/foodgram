from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import views


from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .filters import IngredientFilter, RecipeFilters
from .paginators import PageLimitPagination
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorOrAdminOrReadOnly)
from .serializers import (IngredientSerializer,
                          FollowSerializer,
                          RecipeGetSerializer,
                          RecipeSetSerializer,
                          RecipesShortSerializer,
                          TagSerializer,)
from recipes.models import (BuyRecipe,
                            Ingredient,
                            IngredientRecipe,
                            FavoriteRecipe,
                            Recipe,
                            Tag)
from users.models import Follow

User = get_user_model()

DICT_ERRORS = {
    'subscribe_to_myself': 'Нельзя подписаться на себя!',
    're-subscription': 'Вы уже подписаны на автора!',
    'not_subscription': 'Вы не подписаны на автора!',
    're-recipe': 'Рецепт уже добавлен!',
    'not-recipe': 'Рецепт уже удален!',
}


class UserViewSet(views.UserViewSet):
    """Вьюсет для обьектов класса User."""

    pagination_class = PageLimitPagination

    def get_permissions(self):
        """
        Переопределяем get_permissions для доступа только авторизованным
        пользователям к эндпоинту users/me/.
        """
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=False,
            pagination_class=PageLimitPagination,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Реализация эндпоинта users/subscriptions/ю"""
        user = request.user
        folowing = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(folowing)
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """
        Реализация эндпоинта users/{id}/subscribe/
        """
        user = request.user
        following = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = FollowSerializer(following,
                                          context={'request': request})
            if user == following:
                return Response(
                    {'errors': '{0}'.format(
                        DICT_ERRORS.get('subscribe_to_myself')
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, following=following).exists():
                return Response(
                    {'errors':
                     '{0}'.format(DICT_ERRORS.get('re-subscription'))},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status.HTTP_201_CREATED)
        follower = Follow.objects.filter(user=user, following=following)
        if follower.exists():
            follower.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': '{0}'.format(DICT_ERRORS.get('re-subscription'))},
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
    filter_backends = (IngredientFilter,)
    search_fields = ('^name', )
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов класса Recipe."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilters
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        """Автоматически записываем автора."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSetSerializer

    def add_obj(self, request, pk_obj, model_obj):
        user = request.user
        obj = get_object_or_404(Recipe, pk=pk_obj)
        serializer = RecipesShortSerializer(obj,
                                            context={'request': request})
        if model_obj.objects.filter(user=user, recipe=obj).exists():
            return Response(
                {'errors': '{0}'.format(DICT_ERRORS.get('re-recipe'))},
                status=status.HTTP_400_BAD_REQUEST
            )
        model_obj.objects.create(user=user, recipe=obj)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delate_obj(self, request, pk_obj, model_obj):
        user = request.user
        obj = get_object_or_404(Recipe, pk=pk_obj)
        through_obj = model_obj.objects.filter(user=user,
                                               recipe=obj)
        if through_obj.exists():
            through_obj.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response({'errors':
                         '{0}'.format(DICT_ERRORS.get('not-recipe'))},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """
        Реализация эндпоинта recipe/{id}/favorite/
        """
        if request.method == 'POST':
            return self.add_obj(request, pk, FavoriteRecipe)
        return self.delate_obj(request, pk, FavoriteRecipe)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """
        Реализация эндпоинта recipe/{id}/shopping_cart/
        """
        if request.method == 'POST':
            return self.add_obj(request, pk, BuyRecipe)
        return self.delate_obj(request, pk, BuyRecipe)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """
        Реализация скачивание списка ингридиентов
        """
        qw_st = IngredientRecipe.objects.filter(
            recipe__buy_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',).annotate(amount=Sum('amount'))

        ingredient_list = 'Cписок покупок:'
        for value in qw_st:
            name = value['ingredient__name']
            measurement_unit = value['ingredient__measurement_unit']
            amount = value['amount']
            ingredient_list += f'\n{name} - {amount} {measurement_unit}'
        file = 'ingredient_list'
        response = HttpResponse(
            ingredient_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={file}.pdf'
        return response
