"""Содержит обработчики для эндпойнтов API."""
from django.db.models import Value, OuterRef, Exists, Model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
import django_filters.rest_framework as dj_filters
from djoser.views import TokenCreateView, UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe
from recipes.constants import RECIPES_ORDERING
from recipes.user_utils import (
    user_has_in_list, add_to_list_of_user, remove_from_list_of_user
)
from users.models import User
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, ReducedRecipeSerializer,
    RecipeShoppingCartSerializer, RecipeFavoritesSerializer,
    ExtendedUserSerializer, UserSubscribeSerializer
)
from .filters import IngredientFilterSet, RecipeFilterBackend
from .permissions import RecipesPermission
from .shopping_cart import get_shopping_cart_txt


class GetTokenView(TokenCreateView):
    """Обработчик эндпойнта 'Получить токен авторизации'."""
    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED

        return response


class UserSetActionMixin:
    """Обеспечивает выполнение операций со наборами (списками) пользователя.
    """
    user_set_item_model = NotImplemented

    def add_remove(self, request, pk):
        """Выполняет операции добавления в список
        и исключения из него.
        """
        serializer = self.get_serializer(
            get_object_or_404(self.user_set_item_model, pk=pk),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.method == 'POST':
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(serializer.data)
            )
        
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class UserViewSet(DjoserUserViewSet, UserSetActionMixin):
    """Набор обработчиков, обеспечивающих доступ к ресурсам:
    - 'Пользователи';
    - 'Подписки'.
    """
    user_set_item_model = User

    def get_queryset(self):
        if self.request.path == reverse('users-subscriptions'):
            return self.request.user.subscribed_to.all()

        return super().get_queryset()

    @action(['get'], detail=False, serializer_class=ExtendedUserSerializer,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Обработчик эндпойнта 'Мои подписки'."""
        return self.list(request)

    @action(['post', 'delete'], detail=True,
            serializer_class=UserSubscribeSerializer,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Обработчик эндпойнтов 'Подписаться на пользователя' и
        'Отписаться от пользователя'.
        """
        return self.add_remove(request, id)
        

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


class RecipeViewSet(ModelViewSet, UserSetActionMixin):
    """Набор обработчиков, обеспечивающих доступ к ресурсам:
    - 'Рецепты';
    - 'Список покупок';
    - 'Избранное'.
    """
    serializer_class = RecipeSerializer
    permission_classes = (RecipesPermission,)
    filter_backends = (RecipeFilterBackend,)
    user_set_item_model = Recipe

    def get_queryset(self):
        """Возвращает кверисет для доступа к ресурсу 'Рецепты'."""
        queryset = Recipe.objects.all()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    user.favorites.filter(pk=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    user.shopping_cart.filter(pk=OuterRef('pk'))
                ),
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False), is_in_shopping_cart=Value(False)
            )

        return queryset.order_by(*RECIPES_ORDERING)

    def perform_create(self, serializer):
        """Выполняет операцию создания рецепта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Выполняет операцию изменения рецепта."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            serializer_class=RecipeShoppingCartSerializer)
    def shopping_cart(self, request, pk):
        """Выполненяет операции со списком покупок."""
        return self.add_remove(request, pk)

    @action(detail=True, methods=['post', 'delete'],
            serializer_class=RecipeFavoritesSerializer)
    def favorite(self, request, pk):
        """Выполненяет операции с избранным пользователя."""
        return self.add_remove(request, pk)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Выполненяет операцию 'Скачать список покупок'."""
        return HttpResponse(
            get_shopping_cart_txt(request.user),
            headers={
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Disposition':
                    'attachment; '
                    f'filename="shopping_cart_{request.user.id}.txt"',
            }
        )
