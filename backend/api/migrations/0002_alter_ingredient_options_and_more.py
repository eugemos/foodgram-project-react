# Generated by Django 4.2.2 on 2023-06-20 07:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': 'ингредиент', 'verbose_name_plural': 'ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientoccurence',
            options={'ordering': ['ingredient'], 'verbose_name': 'использование ингредиента', 'verbose_name_plural': 'использования ингредиентов'},
        ),
        migrations.AlterModelOptions(
            name='receipe',
            options={'ordering': ['name'], 'verbose_name': 'рецепт', 'verbose_name_plural': 'рецепты'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name'], 'verbose_name': 'тег', 'verbose_name_plural': 'теги'},
        ),
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