from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from recipes.models import (BuyRecipe,
                            Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            Tag)
from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmins(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('username', 'email')


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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )


admin.site.register(BuyRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(Follow)
