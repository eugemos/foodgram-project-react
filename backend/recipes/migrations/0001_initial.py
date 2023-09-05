# Generated by Django 4.2.4 on 2023-09-05 16:49

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=20, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('text', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='recipe', verbose_name='Иллюстрация')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Это значение должно быть больше нуля.')], verbose_name='Время приготовления, мин.')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'рецепты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Название')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(regex='\\A#[0-9a-fA-F]{6}\\Z')], verbose_name='Цветовой HEX-код')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'тег',
                'verbose_name_plural': 'теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RecipeInShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'рецепт в корзине',
                'verbose_name_plural': 'рецепты в корзине',
            },
        ),
        migrations.CreateModel(
            name='RecipeInFavorites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'рецепт в избранном',
                'verbose_name_plural': 'рецепты в избранном',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='in_favorites',
            field=models.ManyToManyField(blank=True, related_name='favorites', through='recipes.RecipeInFavorites', to=settings.AUTH_USER_MODEL, verbose_name='В избранных рецептах у пользователей'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='in_shopping_cart',
            field=models.ManyToManyField(blank=True, related_name='shopping_cart', through='recipes.RecipeInShoppingCart', to=settings.AUTH_USER_MODEL, verbose_name='В списке покупок у пользователей'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.tag', verbose_name='Теги'),
        ),
        migrations.CreateModel(
            name='IngredientOccurence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Это значение должно быть больше нуля.')], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recipes', to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'использование ингредиента',
                'verbose_name_plural': 'использования ингредиентов',
                'ordering': ('ingredient',),
            },
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='recipeinshoppingcart',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_shopping_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipeinfavorites',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='ingredientoccurence',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_occurence'),
        ),
    ]
