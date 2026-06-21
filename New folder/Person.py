class Person:
    def __init__(self, name):
        self.name = name
        self._ordered_items = []   

    def add_item(self, food_item):
        self._ordered_items.append(food_item)

    def get_items(self):
        return self._ordered_items

    def __str__(self):
        return f"Person: {self.name}, Orders: {self._ordered_items}"
