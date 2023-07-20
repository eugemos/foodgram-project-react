import django_filters.rest_framework as dj_filters
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Tag, Ingredient, Receipe
from .serializers import TagSerializer, IngredientSerializer, ReceipeSerializer
from .filters import IngredientFilterSet
from .permissions import ReceipesPermission

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


class ReceipeViewSet(ModelViewSet):
    """
    ViewSet for viewing receipes.
    """
    queryset = Receipe.objects.all()
    serializer_class = ReceipeSerializer
    permission_classes = (ReceipesPermission,)
    # filter_backends = (dj_filters.DjangoFilterBackend,)
    # filterset_class = IngredientFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
