from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Кастомная модель пользователей."""

    username = models.CharField(
        'Ник пользователя',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z',
                           'Недопустимые символы в username!')
        ]
    )

    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('Адрес электронной почты',
                              max_length=254,
                              unique=True,
                              )
    password = models.CharField('Пароль', max_length=254)
    avatar = models.ImageField('Аватар пользователя',
                               upload_to='users/avatars/', blank=True)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} {self.email}'


class Follow(models.Model):
    """Модель для подписок на других пользователей."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='following')

    class Meta:
        ordering = ['user']
        verbose_name = 'Подписка на пользователей'
        verbose_name_plural = 'Подписки на пользователей'

    def __str__(self):
        return f'{self.user} follows {self.following}'
