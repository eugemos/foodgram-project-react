class Ingredient:
    def __init__(self, occurence):
        self.name = occurence.ingredient.name
        self.measurement_unit = occurence.ingredient.measurement_unit
        self.amount = occurence.amount

    def add_amount(self, occurence):
        self.amount += occurence.amount

    def __str__(self):
        return f'{self.name}, {self.measurement_unit} - {self.amount}' 


class ShoppingCart:
    def __init__(self, user):
        self.cart = {}
        for recipe in user.shopping_cart.all():
            for occurence in recipe.ingredients.all():
                key = occurence.ingredient.pk
                if key in self.cart:
                    self.cart[key].add_amount(occurence)
                else:
                    self.cart[key] = Ingredient(occurence)

    def to_text(self):
        lines = [str(ingredient) for ingredient in self.cart.values()]
        lines.append('')
        return '\n'.join(lines)