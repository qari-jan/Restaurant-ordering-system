class Order:
    def __init__(self):
        self._orders = {}   

    def add_order(self, person, food_item):
        person_name = person.name if hasattr(person, "name") else person
        if person_name not in self._orders:
            self._orders[person_name] = []
        self._orders[person_name].append(food_item)

    def calculate_total(self):
        total = 0
        for items in self._orders.values():
            for item in items:
                total += item.get_price()
        return total

    def get_orders(self):
        return self._orders

    def __str__(self):
        return f"Orders: { {person: [item.get_name() for item in items] for person, items in self._orders.items()} }"
