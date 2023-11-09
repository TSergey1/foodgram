from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .filters import IngredientFilter, RecipeFilters
from .paginators import PageLimitPagination
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorOrAdminOrReadOnly)
from .serializers import (BuyRecipe,
                          BuyRecipeSerializer,
                          IngredientSerializer,
                          FavoriteRecipe,
                          FavoriteRecipeSerializer,
                          FollowSerializer,
                          RecipeGetSerializer,
                          RecipeSetSerializer,
                          TagSerializer,)
from recipes.models import (Ingredient,
                            IngredientRecipe,
                            Recipe,
                            Tag)
from users.models import Follow, User


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

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """
        Реализация эндпоинта users/{id}/subscribe/
        """
        following = get_object_or_404(User, pk=id)
        serializer = FollowSerializer(following,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        following = get_object_or_404(User, pk=id)
        get_object_or_404(Follow,
                          user=request.user,
                          following=following).delete()
        return Response(status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name', )
    permission_classes = (IsAdminOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов класса Recipe."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilters
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSetSerializer

    def add_obj(self, request, pk, serializers_name):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializers_name(data={'recipe': recipe.id,
                                            'user': request.user.id},
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

    def delate_obj(self, request, pk, model_name):
        recipe = get_object_or_404(Recipe, pk=pk)
        get_object_or_404(model_name,
                          user=request.user,
                          recipe=recipe).delete()
        return Response(status.HTTP_204_NO_CONTENT)

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """
        Реализация эндпоинта recipe/{id}/favorite/
        """
        return self.add_obj(request, pk, FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delate_obj(request, pk, FavoriteRecipe)

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """
        Реализация эндпоинта recipe/{id}/shopping_cart/
        """
        return self.add_obj(request, pk, BuyRecipeSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
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
            'ingredient__measurement_unit',).annotate(
                amount=Sum('amount')).order_by('ingredient__name')

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
