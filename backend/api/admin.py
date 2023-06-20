from django.contrib import admin

from .models import Tag, Ingredient, Receipe, IngredientOccurence

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Receipe)
admin.site.register(IngredientOccurence)
