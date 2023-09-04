"""Содержит настройки административной панели для приложения recipes."""
from django import forms
from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientOccurence


class RecipeAdminForm(forms.ModelForm):
    pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели Tag в административной панели."""
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в административной панели."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientOccurenceInline(admin.TabularInline):
    """Настройки отображения модели IngredientOccurence в административной
    панели.
    """
    model = IngredientOccurence
    verbose_name = 'Ингредиент в этом рецепте'
    verbose_name_plural = 'Ингредиенты в этом рецепте'
    readonly_fields = ('measurement_unit',)
    fields = ('ingredient', 'amount', 'measurement_unit')

    @admin.display(description='Ед. изм.')
    def measurement_unit(self, occurence):
        return occurence.ingredient.measurement_unit


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения модели Recipe в административной панели."""
    readonly_fields = ('in_favor_count',)
    list_display = ('name', 'author_name')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientOccurenceInline,)
    form = RecipeAdminForm

    @admin.display(description='Автор')
    def author_name(self, recipe):
        """Возвращает имя пользователя автора рецепта."""
        return recipe.author.username

    @admin.display(description='Количество добавлений в избранное')
    def in_favor_count(self, recipe):
        """Возвращает количество добавлений рецепта в избранное."""
        return recipe.in_favore.count()
