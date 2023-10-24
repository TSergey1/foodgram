from django.contrib import admin
from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


# admin.site.register(UserAdmin)

# class UserAdmins(admin.ModelAdmin):
#     list_display = (
#         'username',
#         'email',
#         'first_name',
#         'last_name',
#     )
#     list_editable = (
#         'username',
#         'email',
#         'first_name',
#         'last_name',
#     )
#     search_fields = ('username',)
#     list_filter = ('username', 'email')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    search_fields = ('name', 'author')
    list_filter = ('name', 'tags__slug')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    search_fields = ('name',)
    list_filter = ('name',)
