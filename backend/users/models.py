"""Содержит модели, используемые приложением users."""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


MAX_PASSWORD_LENGTH = 150


class User(AbstractUser):
    """Модель пользователя сайта."""
    password = models.CharField(_('password'), max_length=MAX_PASSWORD_LENGTH)
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        },
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    favorites = models.ManyToManyField(
        'api.Recipe',
        related_name='in_favore',
        verbose_name='Избранные рецепты',
        blank=True,
    )
    shopping_cart = models.ManyToManyField(
        'api.Recipe',
        db_table='ShoppingCart',
        related_name='in_shopping_cart',
        verbose_name='Список покупок',
        blank=True,
    )
    subscribed_to = models.ManyToManyField(
        'self',
        related_name='subscribers',
        symmetrical=False,
        verbose_name='Подписки',
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.username} ({self.email})'

    def has_in_list(self, list_name: str, obj):
        """Возвращает True, если объект obj находится в списке list_name
        пользователя.
        """
        return obj in getattr(self, list_name).all()

    def add_to_list(self, list_name: str, obj):
        """Добавляет объект obj в список list_name пользователя."""
        getattr(self, list_name).add(obj)

    def remove_from_list(self, list_name: str, obj):
        """Удаляет объект obj из списка list_name пользователя."""
        getattr(self, list_name).remove(obj)

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

    def has_in_favore(self, recipe):
        """Возвращает True, если рецепт содержится в избранном
        пользователя.
        """
        return recipe in self.favorites.all()

    def add_to_favorites(self, recipe):
        """Добавляет рецепт в избранное пользователя."""
        self.favorites.add(recipe)

    def remove_from_favorites(self, recipe):
        """Удаляет рецепт из избранного пользователя."""
        self.favorites.remove(recipe)

    def has_in_shopping_cart(self, recipe):
        """Возвращает True, если рецепт содержится в списке покупок
        пользователя.
        """
        return recipe in self.shopping_cart.all()

    def add_to_shopping_cart(self, recipe):
        """Добавляет рецепт в список покупок пользователя."""
        self.shopping_cart.add(recipe)

    def remove_from_shopping_cart(self, recipe):
        """Удаляет рецепт из списка покупок пользователя."""
        self.shopping_cart.remove(recipe)
