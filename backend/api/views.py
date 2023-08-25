"""Содержит обработчики для эндпойнтов API."""
from django.db.models import F, Sum, Value
from django.db.models.lookups import Exact
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
    ExtendedUserSerializer
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


class UserViewSet(DjoserUserViewSet):
    """Набор обработчиков, обеспечивающих доступ к ресурсам:
    - 'Пользователи';
    - 'Подписки'.
    """
    def get_queryset(self):
        if self.request.path == reverse('users-subscriptions'):
            return self.request.user.subscribed_to.all()

        return super().get_queryset()

    @action(['get'], detail=False, serializer_class=ExtendedUserSerializer,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Обработчик эндпойнта 'Мои подписки'."""
        return self.list(request)

    @action(['post'], detail=True, serializer_class=ExtendedUserSerializer,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Обработчик эндпойнта 'Подписаться на пользователя'."""
        author = get_object_or_404(User, pk=id)
        if request.user == author:
            return Response(
                dict(errors='Нельзя подписаться на самого себя.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.is_subscribed_to(author):
            return Response(
                dict(errors='Вы уже подписаны на этого автора.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.subscribe_to(author)
        serializer = self.get_serializer(author)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Обработчик эндпойнта 'Отписаться от пользователя'."""
        author = get_object_or_404(User, pk=id)
        if not request.user.is_subscribed_to(author):
            return Response(
                dict(errors='Вы не подписаны на этого автора.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.unsubscribe_from(author)
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


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
    serializer_class = RecipeSerializer
    permission_classes = (RecipesPermission,)
    filter_backends = (RecipeFilterBackend,)

    def get_queryset(self):
        """Возвращает кверисет для доступа к ресурсу 'Рецепты'."""
        queryset = Recipe.objects.all()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Sum(Exact(F('in_favorites'), user.id),
                                 default=False),
                is_in_shopping_cart=Sum(Exact(F('in_shopping_cart'), user.id),
                                        default=False),
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
        if user_has_in_list(request.user, list_name, recipe):
            return Response(
                dict(errors='Этот рецепт уже есть в этом списке.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        add_to_list_of_user(request.user, list_name, recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_list(self, list_name, request, pk):
        """Выполняет операцию удаления рецепта из списка."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if user_has_in_list(request.user, list_name, recipe):
            remove_from_list_of_user(request.user, list_name, recipe)
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(
            dict(errors='Этого рецепта нет в этом списке.'),
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Обеспечивает выполнение операции 'Скачать список покупок'."""
        return HttpResponse(
            get_shopping_cart_txt(request.user),
            headers={
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Disposition':
                    'attachment; '
                    f'filename="shopping_cart_{request.user.id}.txt"',
            }
        )
