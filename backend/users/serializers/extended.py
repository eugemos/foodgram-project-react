import re

from rest_framework import serializers

from api.serializers import ReducedRecipeSerializer
from .base import UserSerializer


class ExtendedUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, user):
        limit = self.get_recipes_limit()
        count = user.recipes.count()
        return min(limit, count) if limit else count

    def get_recipes(self, user):
        limit = self.get_recipes_limit()
        serializer = ReducedRecipeSerializer(
            user.recipes.all()[0:limit] if limit else user.recipes,
            many=True, context=self.context
        )
        return serializer.data

    def get_recipes_limit(self):
        limit = self.context['request'].query_params.get('recipes_limit', '')
        return int(limit) if re.fullmatch('\d+', limit) else 0

