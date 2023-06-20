import django_filters.rest_framework as dj_filters
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer
from .filters import IngredientFilterSet

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

