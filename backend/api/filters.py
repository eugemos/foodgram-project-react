"""Содержит фильтры, используемые приложением api."""
import re

import django_filters.rest_framework as dj_filters
from rest_framework.filters import BaseFilterBackend

from recipes.models import Ingredient


class IngredientFilterSet(dj_filters.FilterSet):
    """Фильтр для модели Ingredient."""
    name = dj_filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterBackend(BaseFilterBackend):
    """Реализует фильтрацию рецептов."""
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('is_favorited', 0) == '1':
            if request.user.is_authenticated:
                queryset = queryset.filter(in_favore=request.user)
            else:
                queryset = queryset.none()

        if request.query_params.get('is_in_shopping_cart', 0) == '1':
            if request.user.is_authenticated:
                queryset = queryset.filter(in_shopping_cart=request.user)
            else:
                queryset = queryset.none()

        if 'author' in request.query_params:
            author_id = request.query_params['author']
            if re.fullmatch(r'\d+', author_id):
                queryset = queryset.filter(author__id=author_id)
            else:
                queryset = queryset.none()

        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset
