class BillSplitter:
    def __init__(self, orders):
        self.orders = orders   # dictionary: person -> list of ordered items
        self._total = None

    def split_custom(self, menu):
        individual_totals = {}
        for person, items in self.orders.items():
            total = 0
            for item in items:
                if hasattr(item, "get_price"):
                    total += item.get_price()
                elif item in menu:
                    total += menu[item]
                else:
                    print(f"Warning: {item} not found in menu")
            individual_totals[person] = total
        self._total = sum(individual_totals.values())
        return individual_totals

    def split_equal(self):
        if not self.orders:
            return {}
        if self._total is None:
            raise ValueError("Total not calculated yet. Run split_custom first.")
        share = self._total / len(self.orders)
        return {person: share for person in self.orders}

    def get_total(self):
        return self._total

    def set_total(self, new_total):
        if new_total > 0:
            self._total = new_total
        else:
            raise ValueError("Total must be greater than zero")

    def choose_split(self, menu, mode="custom"):
        if mode == "custom":
            return self.split_custom(menu)
        elif mode == "equal":
            if self._total is None:
                self.split_custom(menu)  
            return self.split_equal()
        else:
            raise ValueError("Invalid mode. Choose 'custom' or 'equal'.")
