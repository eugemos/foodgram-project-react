"""Cодержит расширенные сериализаторы, используемые приложением users."""
import re

from rest_framework import serializers

from api.serializers import ReducedRecipeSerializer
from .base import UserSerializer


class ExtendedUserSerializer(UserSerializer):
    """Сериализатор для модели User, расширенный включеием информации о
    рецептах данного пользователя.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, user):
        """Возвращает значение для поля recipes_count."""
        limit = self.get_recipes_limit()
        count = user.recipes.count()
        return min(limit, count) if limit else count

    def get_recipes(self, user):
        """Возвращает значение для поля recipes."""
        limit = self.get_recipes_limit()
        serializer = ReducedRecipeSerializer(
            user.recipes.all()[0:limit] if limit else user.recipes,
            many=True, context=self.context
        )
        return serializer.data

    def get_recipes_limit(self):
        """Возвращает значение параметра recipes_limit из строки запроса,
        если он там есть. В противном случае - 0.
        """
        limit = self.context['request'].query_params.get('recipes_limit', '')
        return int(limit) if re.fullmatch(r'\d+', limit) else 0
