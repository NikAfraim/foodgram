from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import (LIMIT_CHAR_7, LIMIT_CHAR_200,
                               LIMIT_CHAR_150, LIMIT_CHAR_254)


class User(AbstractUser):
    """Кастомная модель User."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=LIMIT_CHAR_150,
        unique=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=LIMIT_CHAR_150
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=LIMIT_CHAR_254,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LIMIT_CHAR_150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LIMIT_CHAR_150,
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscriber',
            )
        ]
