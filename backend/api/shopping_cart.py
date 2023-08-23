"""Содержит классы, отвечающие за формирование списка покупок в текстовом
виде.
"""


def get_shopping_cart_txt(user):
    """Возвращает список покупок заданного пользователя в текстовом виде."""
    cart = ShoppingCart(user)
    return cart.to_text()


class Ingredient:
    """Представляет ингредиент в списке покупок."""
    def __init__(self, occurence):
        """Инициализирует ингредиент в списке покупок."""
        self.name = occurence.ingredient.name
        self.measurement_unit = occurence.ingredient.measurement_unit
        self.amount = occurence.amount

    def add_amount(self, occurence):
        """Увеличивает количество ингредиента в списке покупок."""
        self.amount += occurence.amount

    def __str__(self):
        return f'{self.name}, {self.measurement_unit} - {self.amount}'


class ShoppingCart:
    """Представляет список покупок."""
    def __init__(self, user):
        """Создаёт список покупок на основании поля shopping_cart объекта
        модели User.
        """
        self.cart = {}
        for recipe in user.shopping_cart.all():
            for occurence in recipe.ingredients.all():
                key = occurence.ingredient.pk
                if key in self.cart:
                    self.cart[key].add_amount(occurence)
                else:
                    self.cart[key] = Ingredient(occurence)

    def to_text(self):
        """Возвращает текстовое представление списка покупок."""
        if self.cart:
            lines = [str(ingredient) for ingredient in self.cart.values()]
            lines.append('')
            return '\n'.join(lines)

        return 'Ваш список покупок пуст.\n'
