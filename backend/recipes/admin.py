"""Содержит настройки административной панели для приложения recipes."""
from django import forms
from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe, IngredientOccurence,
    RecipeInFavorites, RecipeInShoppingCart
)


class IngredientOccurenceAdminFormSet(forms.BaseInlineFormSet):
    """Формсет для отображения ингредиентов внутри рецепта."""
    default_error_messages = dict(
        too_few_forms='Рецепт должен содержать хотя бы один ингредиент.'
    )


class IngredientOccurenceInline(admin.TabularInline):
    """Настройки отображения в административной панели ингредиентов
    внутри рецепта.
    """
    formset = IngredientOccurenceAdminFormSet
    model = IngredientOccurence
    extra = 0
    min_num = 1
    verbose_name = 'ингредиент в этом рецепте'
    verbose_name_plural = 'ингредиенты в этом рецепте'
    readonly_fields = ('measurement_unit',)
    fields = ('ingredient', 'amount', 'measurement_unit')

    @admin.display(description='Ед. изм.')
    def measurement_unit(self, occurence):
        return occurence.ingredient.measurement_unit

    def get_formset(self, request, obj=None, **kwargs):
        kwargs.update(validate_min=True)
        return super().get_formset(request, obj, **kwargs)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения модели Recipe в административной панели."""
    readonly_fields = ('in_favor_count',)
    exclude = ('in_favorites', 'in_shopping_cart')
    inlines = (IngredientOccurenceInline,)
    list_display = ('name', 'author_name')
    list_filter = ('author', 'name', 'tags')

    @admin.display(description='Автор')
    def author_name(self, recipe):
        """Возвращает имя пользователя автора рецепта."""
        return recipe.author.username

    @admin.display(description='Количество добавлений в избранное')
    def in_favor_count(self, recipe):
        """Возвращает количество добавлений рецепта в избранное."""
        return recipe.in_favorites.count()


@admin.register(RecipeInFavorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Настройки отображения модели RecipeInFavorites
    в административной панели.
    """
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')


@admin.register(RecipeInShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки отображения модели RecipeInShoppingCart
    в административной панели.
    """
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели Tag в административной панели."""
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в административной панели."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
