from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


MAX_PASSWORD_LENGTH = 150

class User(AbstractUser):
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
    )
    shopping_cart = models.ManyToManyField(
        'api.Recipe',
        db_table='ShoppingCart',
        related_name='in_shopping_cart',
        verbose_name='Список покупок',
    )
    subscribed_to=models.ManyToManyField(
        'self',
        related_name='subscribers',
        symmetrical=False,
        verbose_name='Подписки'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.username} ({self.email})'

    def is_subscribed_to(self, user):
        return user in self.subscribed_to.all()

    def subscribe_to(self, user):
        self.subscribed_to.add(user)

    def unsubscribe_from(self, user):
        self.subscribed_to.remove(user)

    def set_subscriptions(self, users):
        self.subscribed_to.set(users)

    def has_in_favore(self, recipe):
        return recipe in self.favorites.all()

    def add_to_favorites(self, recipe):
        self.favorites.add(recipe)

    def remove_from_favorites(self, recipe):
        self.favorites.remove(recipe)

    def has_in_shopping_cart(self, recipe):
        return recipe in self.shopping_cart.all()

    def add_to_shopping_cart(self, recipe):
        self.shopping_cart.add(recipe)

    def remove_from_shopping_cart(self, recipe):
        self.shopping_cart.remove(recipe)

