from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import CONST
from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(
        max_length=CONST['max_legth_charfield'],
        unique=True,
        validators=[validate_username],
        verbose_name='Юзернейм',
    )
    email = models.EmailField(
        max_length=CONST['max_legth_email'],
        unique=True
    )
    first_name = models.CharField(
        max_length=CONST['max_legth_charfield'],
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=CONST['max_legth_charfield'],
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=CONST['max_legth_charfield'],
        verbose_name='Пароль'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки на пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
