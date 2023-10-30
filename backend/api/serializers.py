import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Ingredient,
                            Recipe,
                            Tag)
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверка подписки у пользователя."""
        user = self.context['request'].user
        if user.is_anonymous or user == obj:
            return False
        return user.follower.filter(following=obj).exists()


class RecipesForFollowSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для сериализатора пользователя User."""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписчиков User."""

    recipes = RecipesForFollowSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_is_subscribed(self, obj):
        """Обозначение подписки пользователя."""
        return True

    def get_recipes_count(self, obj):
        """Количество подписок у пользователя."""
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов Tag."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class Base64ImageField(serializers.ImageField):
    """Конвертация base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов Recipe для GET запросов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        # read_only_fields = ('id',
        #                     'is_favorited',
        #                     'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        """Проверка рецепта в избранных у пользователя у пользователя."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка рецепта в покупках у пользователя у пользователя."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.buy_user.filter(recipe=obj).exists()


# class RecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор рецептов Recipe для POST, PATCH запросов."""

#     class Meta:
#         model = Recipe
#         fields = ('ingredients',
#                   'tags',
#                   'image',
#                   'is_favorited',
#                   'is_in_shopping_cart',
#                   'name',
#                   'text',
#                   'cooking_time')


# class RecipeSerializer(serializers.ModelSerializer):

#     image = Base64ImageField()
#     image_url = serializers.SerializerMethodField(
#         'get_image_url',
#         read_only=True,
#     )

#     class Meta:
#         model = Recipe
#         fields = ('image', 'image_url')

#     def get_image_url(self, obj):
#         if obj.image:
#             return obj.image.url
#         return None
