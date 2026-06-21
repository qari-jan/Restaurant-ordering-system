import datetime
from Person import Person
from Food_Item import FoodItem
from Order import Order
from Bill_Splitter import BillSplitter

# --- Load Menu from File ---
def load_menu():
    menu = {}
    with open("menu.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 2:
                continue
            item, price = parts
            menu[item] = int(price)
    return menu

menu = load_menu()

# --- Show Menu ---
def show_menu():
    print("\n--- Available Menu ---")
    print(f"{'Item':<12} | {'Price (Rs)':<10}")
    print("-" * 25)
    for item, price in menu.items():
        print(f"{item:<12} | {price:<10}")
    print("-" * 25)

show_menu()

# --- User Orders ---
num_members = int(input("\nEnter number of members: "))
persons = []
orders = Order()

for i in range(num_members):
    name = input(f"\nEnter name of member {i+1}: ")
    person = Person(name)

    while True:
        item = input(f"Enter food item for {name} (or type 'no' to finish): ")
        if item.lower() == "no":
            break

        normalized_item = None
        for key in menu.keys():
            if key.lower() == item.lower():
                normalized_item = key
                break

        if normalized_item is None:
            print(f"Warning: {item} not found in menu, try again.")
            continue

        food_item = FoodItem(normalized_item, menu[normalized_item])
        person.add_item(food_item)
        orders.add_order(person, food_item)

    persons.append(person)

# --- Bill Calculation ---
total = orders.calculate_total()
bill_splitter = BillSplitter({
    person.name: [item.get_name() for item in orders.get_orders()[person.name]]
    for person in persons
})

mode = input("\nChoose split mode (custom/equal): ").lower()
shares = bill_splitter.choose_split(menu, mode)

# --- Timestamp ---
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Print Report ---
print("\n--- Final Bill Report ---")
print(f"Timestamp: {timestamp}")
print(f"{'Name':<12} | {'Items Ordered':<20} | {'Amount':<6}")
print("-" * 45)
report_lines = []
for person in persons:
    items = ", ".join([item.get_name() for item in person.get_items()])
    amount = shares[person.name]
    line = f"{person.name:<12} | {items:<20} | Rs.{amount:<6}"
    print(line)
    report_lines.append(line)
print("-" * 45)
print(f"Total Bill: Rs.{total}")

# --- Save Report to File ---
with open("bill.txt", "a") as f:
    f.write("\n--- New Order Session ---\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"{'Name':<12} | {'Items Ordered':<20} | {'Amount':<6}\n")
    f.write("-" * 45 + "\n")
    for line in report_lines:
        f.write(line + "\n")
    f.write("-" * 45 + "\n")
    f.write(f"Total Bill: Rs.{total}\n")

print("\nBill report appended to 'bill.txt'")