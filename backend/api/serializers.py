import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (BuyRecipe,
                            Ingredient,
                            IngredientRecipe,
                            FavoriteRecipe,
                            Recipe,
                            Tag)

User = get_user_model() 


DICT_ERRORS2 = {
    'not_ingredient': 'Должен быть хотя бы один ингридиент!',
    're_ingredien': 'Ингридиенты должны быть уникальными',
    'null_ingredien': 'Значение должно быть больше 0',


    're-recipe': 'Рецепт уже добавлен!',
    'not-recipe': 'Рецепт уже удален!',
}


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
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.follower.filter(following=obj).exists()


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов короткий."""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)
        read_only_fields = ('__all__',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписчиков User."""

    recipes = RecipesShortSerializer(many=True, read_only=True)
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
        read_only_fields = ('__all__',)

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


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов Recipe для GET запросов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
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
        read_only_fields = ('__all__',)

    def get_ingredients(self, obj):
        """Получение ингридиентов."""
        return obj.ingredients.values('id',
                                      'name',
                                      'measurement_unit',
                                      amount=F('recipe__amount'))

    def get_is_favorited(self, obj):
        """Проверка рецепта в избранных у пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка рецепта в покупках у пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return BuyRecipe.objects.filter(
            user=user, recipe=obj
        ).exists()


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента при создании рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id',
                  'amount',)


class RecipeSetSerializer(serializers.ModelSerializer):
    """Сериализатор Recipe для POST, PATCH запросов."""

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': '{0}'.format(DICT_ERRORS2.get('not_ingredient'))})
        ingredient_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    '{0}'.format(DICT_ERRORS2.get('re_ingredien'))
                )
            ingredient_list.append(ingredient)
            if int(item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients':
                    ('{0}'.format(DICT_ERRORS2.get('null_ingredien')))
                })
        data['ingredients'] = ingredients
        return data

    def get_ingredient(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient.get('id'))
            IngredientRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=recipe,
                amount=ingredient.get('amount'))

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.get_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_list = self.initial_data.get('tags')
        instance.tags.set(tags_list)

        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        ingredient_list = validated_data.get('ingredients')
        self.get_ingredient(instance, ingredient_list)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeGetSerializer(instance, context={"request": request}).data
