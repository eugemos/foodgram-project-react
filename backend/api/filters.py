import django_filters.rest_framework as dj_filters

from .models import Ingredient


class IngredientFilterSet(dj_filters.FilterSet):
    name = dj_filters.CharFilter(field_name="name", lookup_expr='istartswith')
    class Meta:
        model = Ingredient
        fields = ('name',)
