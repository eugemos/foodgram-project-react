"""Содержит обработчики для эндпойнтов приложения api."""
import re

from django.http import HttpResponse
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
from .shopping_cart import ShoppingCart


class TagViewSet(ReadOnlyModelViewSet):
    """Набор обработчиков, обеспечивающих доступ к ресурсу 'Теги'."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Набор обработчиков, обеспечивающих доступ к ресурсу 'Ингредиенты'."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class RecipeViewSet(ModelViewSet):
    """Набор обработчиков, обеспечивающих доступ к ресурсам:
    - 'Рецепты';
    - 'Список покупок';
    - 'Избранное'.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (RecipesPermission,)

    def get_queryset(self):
        """Возвращает кверисет для доступа к ресурсу 'Рецепты'
        с учётом параметров строки запроса.
        """
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

        tags = self.request.query_params.getlist('tags')
        if tags:
            qs = qs.filter(tags__slug__in=tags).distinct()

        return qs

    def perform_create(self, serializer):
        """Выполняет операцию создания рецепта."""
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        """Выполняет операцию изменения рецепта."""
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Выполняет операцию частичного изменения рецепта."""
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=[],
            serializer_class=ReducedRecipeSerializer)
    def shopping_cart(self, request, pk):
        """Обеспечивает общий доступ к ресурсу 'Список покупок'."""
        pass

    @shopping_cart.mapping.post
    def add_to_shopping_cart(self, request, pk):
        """Обеспечивает выполнение операции
        'Добавить рецепт в список покупок'.
        """
        return self.add_to_list('shopping_cart', request, pk)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk):
        """Обеспечивает выполнение операции
        'Удалить рецепт из списка покупок'.
        """
        return self.remove_from_list('shopping_cart', request, pk)

    @action(detail=True, methods=[],
            serializer_class=ReducedRecipeSerializer)
    def favorite(self, request, pk):
        """Обеспечивает общий доступ к ресурсу 'Избранное'."""
        pass

    @favorite.mapping.post
    def add_to_favorites(self, request, pk):
        """Обеспечивает выполнение операции
        'Добавить рецепт в избранное'.
        """
        return self.add_to_list('favorites', request, pk)

    @favorite.mapping.delete
    def remove_from_favorites(self, request, pk):
        """Обеспечивает выполнение операции
        'Удалить рецепт из избранного'.
        """
        return self.remove_from_list('favorites', request, pk)

    def add_to_list(self, list_name, request, pk):
        """Выполняет операцию добавления рецепта в список."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if user.has_in_list(list_name, recipe):
            return Response(
                dict(errors='Этот рецепт уже есть в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        user.add_to_list(list_name, recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_list(self, list_name, request, pk):
        """Выполняет операцию удаления рецепта из списка."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if user.has_in_list(list_name, recipe):
            user.remove_from_list(list_name, recipe)
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(
                dict(errors='Этого рецепта нет в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Обеспечивает выполнение операции 'Скачать список покупок'."""
        user = request.user
        cart = ShoppingCart(user)
        return HttpResponse(
            cart.to_text(),
            headers={
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Disposition':
                    f'attachment; filename="shopping_cart_{user.id}.txt"',
            }
        )
