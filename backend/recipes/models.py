"""Содержит модели, используемые приложением recipes."""
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

from recipes import const


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        'Название', max_length=const.MAX_TAG_NAME_LENGTH, unique=True
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=const.TAG_COLOR_CODE_LENGTH,
        unique=True,
        validators=(
            RegexValidator(regex=const.TAG_COLOR_CODE_REGEXP),
        ),
    )
    slug = models.SlugField('Slug', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        'Название', max_length=const.MAX_INGREDIENT_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=const.MAX_INGREDIENT_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецепта."""
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    name = models.CharField(
        'Название', max_length=const.MAX_RECIPE_NAME_LENGTH
    )
    text = models.TextField('Описание')
    image = models.ImageField('Иллюстрация', upload_to='recipe')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=(
            MinValueValidator(1, 'Это значение должно быть больше нуля.'),
        )
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )

    class Meta:
        ordering = const.RECIPES_ORDERING
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return f'{self.name}'

    def add_ingredients(self, ingredient, amount=None):
        """Добавляет ингредиенты в рецепт."""
        if isinstance(ingredient, Ingredient):
            occurences = (dict(ingredient=ingredient, amount=amount),)
        else:
            occurences = ingredient

        IngredientOccurence.objects.bulk_create(
            IngredientOccurence(
                recipe=self,
                ingredient=occurence['ingredient'],
                amount=occurence['amount']
            )
            for occurence in occurences
        )

    def set_tags(self, tags):
        """Устанавливает набор тегов для рецепта."""
        self.tags.set(tags)


class IngredientOccurence(models.Model):
    """Модель, представляющая вхождение ингредиента в рецепт."""
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(1, 'Это значение должно быть больше нуля.'),
        )
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'использование ингредиента'
        verbose_name_plural = 'использования ингредиентов'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'
