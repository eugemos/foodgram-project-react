import re

from django.shortcuts import get_object_or_404
import django_filters.rest_framework as dj_filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Tag, Ingredient, Recipe
from .serializers import (
    TagSerializer, IngredientSerializer, 
    RecipeSerializer, ReducedRecipeSerializer
)
from .filters import IngredientFilterSet
from .permissions import RecipesPermission


class TagViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing ingredients.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class RecipeViewSet(ModelViewSet):
    """
    ViewSet for viewing receipes.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (RecipesPermission,)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if self.request.query_params.get('is_favorited', 0) == '1':
            if user.is_authenticated:
                qs = qs.filter(in_favore=user)
            else:
                qs = qs.none()

        if self.request.query_params.get('is_in_shopping_cart', 0) == '1':
            if user.is_authenticated:
                qs = qs.filter(in_shopping_cart=user)
            else:
                qs = qs.none()

        if 'author' in self.request.query_params:
            author_id = self.request.query_params['author']
            if re.fullmatch('\d+', author_id):
                qs = qs.filter(author__id=author_id)
            else:
                qs = qs.none()

        for tag in self.request.query_params.getlist('tags'):
            qs = qs.filter(tags__slug=tag)

        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'],
            serializer_class=ReducedRecipeSerializer)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if user.has_in_shopping_cart(recipe):
            return Response(
                dict(errors='Этот рецепт уже есть в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        user.add_to_shopping_cart(recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if user.has_in_shopping_cart(recipe):
            user.remove_from_shopping_cart(recipe)
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(
                dict(errors='Этого рецепта нет в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=[],
            serializer_class=ReducedRecipeSerializer)
    def favorite(self, request, pk):
        pass

    @favorite.mapping.post
    def add_to_favorites(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if user.has_in_favore(recipe):
            return Response(
                dict(errors='Этот рецепт уже есть в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        user.add_to_favorites(recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_from_favorites(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if user.has_in_favore(recipe):
            user.remove_from_favorites(recipe)
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(
                dict(errors='Этого рецепта нет в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )
