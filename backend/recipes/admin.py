from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (BuyRecipe,
                            Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            Tag)
from users.models import Follow, User


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag

    def clean(self):
        cleaned_data = super(Tag, self).clean()
        # if cleaned_data.get('color'):
        #     raise ValidationError(u'Нужно выбрать что-то одно')
        return cleaned_data


@admin.register(User)
class UserAdmins(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'count_follow',
        'count_recipe',
    )
    list_filter = ('username', 'email')
    search_fields = ('username',)

    def count_follow(self, obj):
        return obj.following.count()

    def count_recipe(self, obj):
        return obj.recipes.count()
    count_follow.short_description = 'Кол-во подписчиков'
    count_recipe.short_description = 'Кол-во рецептов'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'count_favorites',
    )
    list_filter = ('author', 'name', 'tags')

    def count_favorites(self, obj):
        return obj.favorites.count()
    count_favorites.short_description = 'Кол-во избранных'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    form = TagForm


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(BuyRecipe)
admin.site.register(FavoriteRecipe)
admin.site.empty_value_display = 'Не задано'
