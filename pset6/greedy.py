import cs50

while True:
    print("O hai! How much change is owed?")
    change = cs50.get_float()
    if change > 0:
        break

Cents = round(change * 100)
Quarters = (Cents - (Cents % 25)) / 25
Cents = Cents - Quarters * 25
Dimes = (Cents - (Cents % 10)) / 10
Cents = Cents - Dimes * 10
Nickel = (Cents - (Cents % 5)) / 5
Cents = Cents - Nickel * 5
Counter = Quarters + Dimes + Nickel + Cents

print (Counter)
