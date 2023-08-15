from rest_framework import serializers

from api.serializers import ReducedRecipeSerializer
from .base import UserSerializer

class ExtendedUserSerializer(UserSerializer):
    recipes = ReducedRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, user):
        return user.recipes.count()
