from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Tag, Ingredient, Recipe, IngredientOccurence


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientOccurenceSerialiser(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientOccurence
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientOccurenceSerialiser(
        required=True, many=True, allow_empty=False)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'name', 'text', 'cooking_time')
        extra_kwargs = {'tags': {'allow_empty': True}}

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for occurence in ingredients:
            IngredientOccurence.objects.create(
                ingredient=occurence['ingredient'],
                recipe=recipe,
                amount=occurence['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        instance = super().update(instance, validated_data)
        recipe.tags.set(tags)
        # instance.ingredients.clear()
        IngredientOccurence.objects.filter(recipe=instance).delete()
        for occurence in ingredients:
            IngredientOccurence.objects.create(
                ingredient=occurence['ingredient'],
                recipe=receipe,
                amount=occurence['amount']
            )

        return instance
