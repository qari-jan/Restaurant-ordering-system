class FoodItem:
    def __init__(self, item_name, price):
        self._item_name = item_name
        self._price = price if price > 0 else 0 

    def get_name(self):
        return self._item_name

    def get_price(self):
        return self._price

    def set_price(self, new_price):
        if new_price > 0:
            self._price = new_price
        else:
            raise ValueError("Price must be greater than zero")

    def __str__(self):
        return f"{self._item_name}: Rs.{self._price}"
