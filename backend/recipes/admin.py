from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'bio'
    )
    list_editable = (
        'email',
        'role',
        'first_name',
        'last_name',
        'bio'
    )
    search_fields = ('username',)
    list_filter = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category',
    )
    search_fields = ('name', 'year', 'category')
    list_filter = ('category', 'year')
    empty_value_display = '-пусто-'
    filter_horizontal = ['genre']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'text',
        'author',
        'pub_date',
        'score',
    )
    search_fields = ('name', 'year', 'category')
    list_filter = ('author', 'score')
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'pub_date',
        'text',
        'review',
    )
    search_fields = ('author', 'review', )
    list_filter = ('author',)
    empty_value_display = '-пусто-'