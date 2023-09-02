"""Содержит сериализаторы, используемые приложением api."""
from base64 import b64decode
import re

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer,
    SetPasswordSerializer as DjoserSetPasswordSerializer,
)
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, IngredientOccurence
import recipes.serializers
from users.constants import MAX_PASSWORD_LENGTH
from users.models import User


IngredientSerializer = recipes.serializers.IngredientSerializer


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
        style={'input_type': 'password'},
        max_length=MAX_PASSWORD_LENGTH
    )


class Base64ImageField(serializers.FileField):
    """Поле для представления файла, загружаемого на сайт в формате base64."""
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
    """Поле для представления иллюстрации к рецепту."""
    file_name_base = 'recipe'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientOccurenceSerialiser(serializers.ModelSerializer):
    """Сериализатор для модели IngredientOccurence."""
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


class TagField(TagSerializer):
    """Поле для представления модели Tag в составе других объектов."""
    def to_internal_value(self, data):
        try:
            return Tag.objects.get(pk=data)
        except ValueError:
            raise serializers.ValidationError(
                ['Идентификатор тега должен быть целым числом.']
            )
        except Tag.DoesNotExist:
            raise serializers.ValidationError(
                ['Тег с таким идентификатором не найден.']
            )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    image = RecipeImageField(required=True)
    tags = TagField(
        required=True, many=True, allow_empty=False,
    )
    ingredients = IngredientOccurenceSerialiser(
        required=True, many=True, allow_empty=False
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'name', 'text', 'cooking_time', 'image',
            'is_favorited', 'is_in_shopping_cart'
        )

    def create(self, validated_data):
        """Создаёт объект типа Recipe."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.set_tags(tags)
        recipe.add_ingredients(ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Изменяет объект типа Recipe."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.all().delete()
        instance.add_ingredients(ingredients)
        return instance


class ReducedRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для представления модели Recipe в составе других
    объектов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class ExtendedUserSerializer(UserSerializer):
    """Сериализатор для модели User, расширенный включением информации о
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


class UserSubscribeSerializer(ExtendedUserSerializer):
    """Сериализатор для использования при подписке и отписке.
    """
    class Meta(ExtendedUserSerializer.Meta):
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        user = self.context['request'].user
        if self.context['request'].method == 'POST':
            if user == self.instance:
                raise serializers.ValidationError(
                    dict(errors='Нельзя подписаться на самого себя.'),
                )

            if user.is_subscribed_to(self.instance):
                raise serializers.ValidationError(
                    dict(errors='Вы уже подписаны на этого автора.'),
                )

        else:
            if not user.is_subscribed_to(self.instance):
                raise serializers.ValidationError(
                    dict(errors='Вы не подписаны на этого автора.'),
                )
        
        return data

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if self.context['request'].method == 'POST':
            user.subscribe_to(instance)
        else:
            user.unsubscribe_from(instance)
            
        return instance    
        