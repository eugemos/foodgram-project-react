# Generated by Django 4.2.2 on 2023-06-20 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_ingredient_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='receipes', through='api.IngredientOccurence', to='api.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='ingredientoccurence',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientoccurence',
            name='receipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.receipe', verbose_name='Рецепт'),
        ),
    ]