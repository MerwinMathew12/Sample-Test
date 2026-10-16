import balance
def deposit():

    amount = float(input("Enter the amount to deposit: "))

    if amount > 0:

        balance.balance += amount

        print("₹", amount, "has been deposited")
        print("New balance: ₹", balance.balance, )

    else:

        print("Enter a valid amount")