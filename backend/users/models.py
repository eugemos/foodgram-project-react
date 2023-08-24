"""Содержит модели, используемые приложением users."""
from django.db import models
from django.contrib.auth.models import AbstractUser

from users import const


class User(AbstractUser):
    """Модель пользователя сайта."""
    password = models.CharField(
        'Пароль', max_length=const.MAX_PASSWORD_LENGTH
    )
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        },
    )
    first_name = models.CharField(
        'Имя', max_length=const.MAX_FIRST_NAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия', max_length=const.MAX_LAST_NAME_LENGTH
    )
    subscribed_to = models.ManyToManyField(
        'self',
        related_name='subscribers',
        symmetrical=False,
        verbose_name='Подписки',
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.username} ({self.email})'

    def is_subscribed_to(self, author):
        """Возвращает True, если пользователь подписан на заданного
        автора.
        """
        return author in self.subscribed_to.all()

    def subscribe_to(self, author):
        """Подписывает пользователя на заданного автора."""
        self.subscribed_to.add(author)

    def unsubscribe_from(self, author):
        """Отписывает пользователя от заданного автора."""
        self.subscribed_to.remove(author)

    def set_subscriptions(self, authors):
        """Задаёт множество подписок пользователя."""
        self.subscribed_to.set(authors)
