from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, user):
        client_user = self.context['request'].user
        return client_user.is_authenticated and client_user.is_subscribed_to(user)

