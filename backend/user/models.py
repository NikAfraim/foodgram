from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель User."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)

    @property
    def is_admin(self):
        return self.is_superuser


class Follow(models.Model):
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
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

