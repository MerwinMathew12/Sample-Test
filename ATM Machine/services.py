from deposit import deposit
from withdraw import withdraw
from check_balance import check_balance
from pin_check import pin_number
from repeat import repeat



def services():

    print("Welcome")
    print("Please Swipe your card")

    card = input("Press Enter to continue or type Yes: ")

    if card == "" or card.lower() in ["yes", "y"]:

        if pin_number():

            print("Card accepted")

            while True:

                print("\nPlease select a service")
                print("1. Check Account balance")
                print("2. Deposit Money")
                print("3. Withdraw Money")

                service = input("Enter your choice: ").lower()

                if service in ["1", "check balance", "balance", "b"]:
                    check_balance()

                elif service in ["2", "deposit", "d"]:
                    deposit()

                elif service in ["3", "withdraw", "w"]:
                    withdraw()

                else:
                    print("Invalid choice")
                    continue

                if repeat() == False:
                    break

    else:
        print("Card not accepted")