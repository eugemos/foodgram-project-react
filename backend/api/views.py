import re

import django_filters.rest_framework as dj_filters
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Tag, Ingredient, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
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
