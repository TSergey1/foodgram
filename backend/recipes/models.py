from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.settings import CONST


User = get_user_model()


class BaseModel(models.Model):
    """Базовая модель."""
    name = models.CharField(
        max_length=CONST['max_legth_tags'],
        db_index=True,
        verbose_name='Название'
    )

    class Meta:
        abstract = True


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=CONST['max_legth_tags'],
        db_index=True,
        unique=True,
        verbose_name='Название'
    )
    color = models.CharField(
        null=True,
        max_length=CONST['max_legth_color'],
        unique=True,
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        verbose_name='Описание',
        null=True,
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(BaseModel):
    """Модель ингридиента."""

    measurement_unit = models.CharField(
        max_length=CONST['max_legth_tags'],
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientRecipe'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Текст',
        help_text='Введите текст'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1),],
        help_text='Введите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Связующая модель ингридиента и рецепта."""

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты',
        related_name='ingredient',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1),],
    )

    class Meta:
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранные рецепты',
        related_name='in_favorites',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_user_recipe_in_favorites'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class BuyRecipe(models.Model):
    """Модель рецептов для покупки."""
    recipe = models.ForeignKey(
        Recipe,
        related_name='buy_recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепты для покупок'
    )
    user = models.ForeignKey(
        User,
        related_name='buy_user',
        on_delete=models.CASCADE,
        verbose_name='Пользователь с покупками'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'
