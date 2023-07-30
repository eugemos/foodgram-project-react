from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer,
    SetPasswordSerializer as DjoserSetPasswordSerializer,
)
from rest_framework import serializers

from users.models import MAX_PASSWORD_LENGTH


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, user):
        client_user = self.context['request'].user
        return client_user.is_authenticated and client_user.is_subscribed_to(user)


class UserCreateSerializer(DjoserUserCreateSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True, 
        max_length=MAX_PASSWORD_LENGTH
    )

    class Meta(DjoserUserCreateSerializer.Meta):
        pass


class SetPasswordSerializer(DjoserSetPasswordSerializer):
    new_password = serializers.CharField(
        style={"input_type": "password"},
        max_length=MAX_PASSWORD_LENGTH        
    )