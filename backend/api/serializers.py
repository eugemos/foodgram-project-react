from base64 import b64decode

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Tag, Ingredient, Recipe, IngredientOccurence


class Base64ImageField(serializers.FileField):
    file_name_base = 'image'

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(
                b64decode(imgstr), 
                name=f'{self.file_name_base}.{ext}'
            )

        return super().to_internal_value(data)


class RecipeImageField(Base64ImageField):
    file_name_base = 'recipe'


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
        source='ingredient', queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )

    class Meta:
        model = IngredientOccurence
        fields = ('id', 'amount', 'measurement_unit', 'name')


class TagField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, instance):
        if isinstance(instance, Tag):
            return dict(
                id=instance.id,
                name=instance.name,
                color=instance.color,
                slug=instance.slug
            )

        return super().to_representation(instance)

class RecipeSerializer(serializers.ModelSerializer):
    image = RecipeImageField(required=True)
    tags = TagField(
        required=True, many=True, allow_empty=False, queryset=Tag.objects.all()
    )
    ingredients = IngredientOccurenceSerialiser(
        required=True, many=True, allow_empty=False
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 
            'name', 'text', 'cooking_time', 'image',
            'is_favorited', 'is_in_shopping_cart'
        )
        extra_kwargs = {
            'cooking_time': {'min_value': 1},
            # 'author': {'read_only': True},
        }

    def get_is_favorited(self, recipe):
        client_user = self.context['request'].user
        return client_user.is_authenticated and client_user.has_in_favore(recipe)

    def get_is_in_shopping_cart(self, recipe):
        client_user = self.context['request'].user
        return client_user.is_authenticated and client_user.has_in_shopping_cart(recipe)

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
