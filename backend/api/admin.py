from django.contrib import admin

from .models import Tag, Ingredient, Receipe, IngredientOccurence


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Receipe)
admin.site.register(IngredientOccurence)
