"""Содержит настройки административной панели для приложения api."""
from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientOccurence


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели Tag в административной панели."""
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в административной панели."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения модели Recipe в административной панели."""
    readonly_fields = ('in_favor_count',)
    list_display = ('name', 'author_name')
    list_filter = ('author', 'name', 'tags')

    @admin.display(description='Автор')
    def author_name(self, recipe):
        """Возвращает имя пользователя автора рецепта."""
        return recipe.author.username

    @admin.display(description='Количество добавлений в избранное')
    def in_favor_count(self, recipe):
        """Возвращает количество добавлений рецепта в избранное."""
        return recipe.in_favore.count()


@admin.register(IngredientOccurence)
class IngredientOccurenceAdmin(admin.ModelAdmin):
    """Настройки отображения модели IngredientOccurence в административной
    панели.
    """
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
