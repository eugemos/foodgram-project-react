from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Tag, Ingredient, Receipe, IngredientOccurence


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class InIngredientOccurenceSerialiser(serializers.Serializer):
    id = serializers.IntegerField()
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # id = PrimaryKeyRelatedField(source='id', queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)
    # class Meta:
    #     model = Ingredient
    #     fields = ('id', 'amount')

# class InIngredientOccurenceSerialiser(ModelSerializer):
#     id = PrimaryKeyRelatedField(source='ingredient', queryset=Ingredient.objects.all())

#     class Meta:
#         model = IngredientOccurence
#         fields = ('id', 'amount')


class InReceipeSerializer(serializers.ModelSerializer):
    ingredients = InIngredientOccurenceSerialiser(
        required=True, many=True, allow_empty=False)

    class Meta:
        model = Receipe
        fields = ('id', 'ingredients', 'tags', 'name', 'text', 'cooking_time')
        extra_kwargs = {'tags': {'allow_empty': True}}

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        receipe = Receipe.objects.create(**validated_data)
        receipe.tags.set(tags)

        for occurence in ingredients:
            receipe.ingredients.add(
                occurence['id'],
                through_defaults={'amount': occurence['amount']}
                # through_defaults={'amount': 1}
            )
            # IngredientOccurence.objects.create(
            #     ingredient=occurence['ingredient'],
            #     receipe=receipe,
            #     amount=occurence['amount']
            # )

        return receipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        receipe = Receipe.objects.create(**validated_data)
        instance = super().update(instance, validated_data)
        receipe.tags.set(tags)
        instance.ingredients.clear()
        for occurence in ingredients:
            # IngredientOccurence.objects.create(
            #     ingredient=occurence['ingredient'],
            #     receipe=receipe,
            #     amount=occurence['amount']
            # )
            receipe.ingredients.add(
                occurence['ingredient'],
                through_defaults={'amount': occurence['amount']}
            )

        return instance
