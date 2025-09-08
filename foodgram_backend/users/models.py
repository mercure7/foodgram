from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from constants import (MAX_EMAIL_LENGTH, MAX_LENGTH_FIRST_NAME,
                       MAX_LENGTH_LAST_NAME, MAX_LENGTH_USERNAME,
                       MAX_PASSWORD_LENGTH)


class User(AbstractUser):
    """Кастомная модель пользователей."""

    username = models.CharField(
        'Ник пользователя',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )

    first_name = models.CharField('Имя', max_length=MAX_LENGTH_FIRST_NAME)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH_LAST_NAME)
    email = models.EmailField('Адрес электронной почты',
                              max_length=MAX_EMAIL_LENGTH,
                              unique=True,
                              )
    password = models.CharField('Пароль', max_length=MAX_PASSWORD_LENGTH)
    avatar = models.ImageField('Аватар пользователя',
                               upload_to='users/avatars/')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} {self.email}'


class Follow(models.Model):
    """Модель для подписок на других пользователей."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Добавленный в подписки пользователь')

    class Meta:
        ordering = ['user']
        unique_together = ['user', 'following']
        constraints = [
            models.CheckConstraint(
                name='Нельзя подписаться на самого себя!',
                check=~models.Q(user=models.F('following'))

            )
        ]
        verbose_name = 'Подписка на пользователей'
        verbose_name_plural = 'Подписки на пользователей'

    def __str__(self):
        return f'{self.user} подписан на - {self.following}'
