import base64
from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from foodgram.constants import DICT_ERRORS
from recipes.models import (BuyRecipe,
                            Ingredient,
                            IngredientRecipe,
                            FavoriteRecipe,
                            Recipe,
                            Tag)
from users.models import Follow, User


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
        return (not (user.is_anonymous or user == obj)
                and user.follower.filter(following=obj).exists())


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов короткий."""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)
        read_only_fields = ('__all__',)


class ShowFollowSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """

    recipes = RecipesShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

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

    def get_recipes_count(self, obj):
        """Количество подписок у пользователя."""
        return obj.recipes.count()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.root.context.get('request')
        if request is not None:
            count = request.query_params.get('recipes_limit')
        else:
            count = self.root.context.get('recipes_limit')
        if count is not None:
            rep['recipes'] = rep['recipes'][:int(count)]
        return rep


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Follow
        fields = ('user',
                  'following',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message='{0}'.format(DICT_ERRORS.get('re-subscription'))
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('following'):
            raise ValidationError(
                '{0}'.format(DICT_ERRORS.get('subscribe_to_myself')),
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        return ShowFollowSerializer(instance.following, context={
            'request': self.context.get('request')
        }).data


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
        return not user.is_anonymous and FavoriteRecipe.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка рецепта в покупках у пользователя."""
        user = self.context.get('request').user
        return not user.is_anonymous and BuyRecipe.objects.filter(
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

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                '{0}'.format(DICT_ERRORS.get('amount_min'))
            )
        elif value > 10000:
            raise serializers.ValidationError(
                '{0}'.format(DICT_ERRORS.get('amount_max'))
            )
        return value


class RecipeSetSerializer(serializers.ModelSerializer):
    """Сериализатор Recipe для POST, PATCH запросов."""

    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        error_messages={
            'does_not_exist': '{0}'.format(DICT_ERRORS.get('tags_not_exist'))
        },
        many=True
    )
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()

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
        read_only_fields = ('author',)

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                '{0}'.format(DICT_ERRORS.get('time_min'))
            )
        elif value > 2000:
            raise serializers.ValidationError(
                '{0}'.format(DICT_ERRORS.get('time_max'))
            )
        return value

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                '{0}'.format(DICT_ERRORS.get('not-tag'))
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                '{0}'.format(DICT_ERRORS.get('tags_not_unique'))
            )

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients':
                '{0}'.format(DICT_ERRORS.get('not_ingredient'))})
        ingredient_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(pk=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    '{0}'.format(DICT_ERRORS.get('not_in-db_ingredient'))
                )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    '{0}'.format(DICT_ERRORS.get('re_ingredient'))
                )
            ingredient_list.append(ingredient)
            if int(item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients':
                    ('{0}'.format(DICT_ERRORS.get('null_ingredient')))
                })
        data['ingredients'] = ingredients
        return data

    @staticmethod
    def get_ingredient(recipe, ingredients):
        ingredients_obj = []
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient.get('id'))
            ingredients_obj.append(
                IngredientRecipe(
                    ingredient=ingredient_obj,
                    amount=ingredient.get('amount'),
                    recipe=recipe
                )
            )
        IngredientRecipe.objects.bulk_create(ingredients_obj)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.get_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.tags.clear()
        tags_list = self.initial_data.get('tags')
        instance.tags.set(tags_list)
        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        ingredient_list = validated_data.pop('ingredients')
        self.get_ingredient(instance, ingredient_list)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(instance, context={'request': request}).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message='{0}'.format(DICT_ERRORS.get('re-recipe'))
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipesShortSerializer(
            instance.recipe,
            context={'request': request},
        ).data


class BuyRecipeSerializer(FavoriteRecipeSerializer):
    """Сериализатор покупок."""

    class Meta:
        model = BuyRecipe
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message='{0}'.format(DICT_ERRORS.get('re-recipe'))
            )
        ]
