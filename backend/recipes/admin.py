"""Содержит настройки административной панели для приложения recipes."""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Tag, Ingredient, Recipe, IngredientOccurence


class IngredientOccurenceAdminFormSet(forms.BaseInlineFormSet):
    # validate_min = True
    def clean(self):
        if any(self.errors):
            return

        if all(self._should_delete_form(form) for form in self.forms):
            raise ValidationError('Нельзя удалить все ингредиенты.')


class IngredientOccurenceInline(admin.TabularInline):
    """Настройки отображения модели IngredientOccurence в административной
    панели.
    """
    # formset = IngredientOccurenceAdminFormSet
    model = IngredientOccurence
    # validate_min = True
    extra = 0
    min_num = 1
    verbose_name = 'Ингредиент в этом рецепте'
    verbose_name_plural = 'Ингредиенты в этом рецепте'
    readonly_fields = ('measurement_unit',)
    fields = ('ingredient', 'amount', 'measurement_unit')

    @admin.display(description='Ед. изм.')
    def measurement_unit(self, occurence):
        return occurence.ingredient.measurement_unit

    def get_formset(self, request, obj=None, **kwargs):
        kwargs.update(
            validate_min=True,
            error_messages=dict(
                too_few_forms='Рецепт должен содержать хотя бы один ингредиент.'
            )
        )
        return super().get_formset(request, obj, **kwargs)


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
    inlines = (IngredientOccurenceInline,)

    @admin.display(description='Автор')
    def author_name(self, recipe):
        """Возвращает имя пользователя автора рецепта."""
        return recipe.author.username

    @admin.display(description='Количество добавлений в избранное')
    def in_favor_count(self, recipe):
        """Возвращает количество добавлений рецепта в избранное."""
        return recipe.in_favore.count()
