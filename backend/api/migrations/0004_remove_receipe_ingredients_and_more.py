# Generated by Django 4.2.2 on 2023-06-20 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_receipe_ingredients_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipe',
            name='ingredients',
        ),
        migrations.AlterField(
            model_name='ingredientoccurence',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receipes', to='api.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientoccurence',
            name='receipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='api.receipe', verbose_name='Рецепт'),
        ),
    ]
