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
        unique=True,
        verbose_name='Название'
    )

    class Meta:
        abstract = True


class Tag(BaseModel):
    """Модель тега."""

    color = models.IntegerField(
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
        ordering = ('name',)
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
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиенты'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Текст',
        help_text='Введите текст'
    )
    cooking_time = models.PositiveIntegerField()(
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
        ordering = ('pub_date',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
