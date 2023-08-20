"""Cодержит базовые сериализаторы, используемые приложением users."""
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer,
    SetPasswordSerializer as DjoserSetPasswordSerializer,
)
from rest_framework import serializers

from users.models import MAX_PASSWORD_LENGTH


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, user):
        """Возвращает значение для поля is_subscribed."""
        client_user = self.context['request'].user
        return (client_user.is_authenticated
                and client_user.is_subscribed_to(user))


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор, используемый при создании нового пользователя."""
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        max_length=MAX_PASSWORD_LENGTH
    )

    class Meta(DjoserUserCreateSerializer.Meta):
        pass


class SetPasswordSerializer(DjoserSetPasswordSerializer):
    """Сериализатор, используемый при изменении пароля пользователя."""
    new_password = serializers.CharField(
        style={"input_type": "password"},
        max_length=MAX_PASSWORD_LENGTH
    )
