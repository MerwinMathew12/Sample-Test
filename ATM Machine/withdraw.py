import balance
def withdraw():

    amount = float(input("Enter amount to withdraw: "))

    if amount <= 0:

        print("Enter a valid amount")

    elif amount <= balance.balance:

        balance.balance -= amount

        print("₹", amount, "has been withdrawn")
        print("Remaining balance: ₹", balance.balance)

    else:

        print("Insufficient balance")