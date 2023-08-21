"""Содержит модели, используемые приложением recipes."""
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Название', max_length=150, unique=True)
    color = models.CharField(
        'Цветовой HEX-код', max_length=7, unique=True,
        validators=(
            RegexValidator(regex=r'\A#[0-9a-fA-F]{6}\Z'),
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
    name = models.CharField('Название', max_length=150)
    measurement_unit = models.CharField('Единица измерения', max_length=20)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецепта."""
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    image = models.ImageField('Иллюстрация', upload_to='recipe')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.'
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
        ordering = ['id']  # ('-pub_date',)  # 
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return f'{self.name}'

    def add_ingredient(self, ingredient, amount):
        """Добавляет ингредиент в рецепт."""
        IngredientOccurence.objects.create(
            recipe=self, ingredient=ingredient, amount=amount
        )

    def set_tags(self, tags):
        """Устанавливает набор тегов для рецепта."""
        self.tags.set(tags)


class IngredientOccurence(models.Model):
    """Модель, представляющая вхождение ингредиента в рецепт."""
    amount = models.PositiveSmallIntegerField('Количество')
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