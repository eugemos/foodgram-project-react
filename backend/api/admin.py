from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientOccurence


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('in_favor_count',)
    list_display = ('name', 'author_name')
    list_filter = ('author', 'name', 'tags')

    @admin.display(description='Автор')
    def author_name(self, recipe):
        return recipe.author.username

    @admin.display(description='Количество добавлений в избранное')
    def in_favor_count(self, recipe):
        return recipe.in_favore.count()
    

@admin.register(IngredientOccurence)
class IngredientOccurenceAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
