"""Содержит фильтры, используемые приложением api."""
import django_filters.rest_framework as dj_filters

from .models import Ingredient


class IngredientFilterSet(dj_filters.FilterSet):
    """Фильтр для модели Ingredient."""
    name = dj_filters.CharFilter(field_name='name', lookup_expr='istartswith')
    class Meta:
        model = Ingredient
        fields = ('name',)
