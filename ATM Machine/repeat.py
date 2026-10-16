def repeat():

    answer = input("Is the process completed? (yes/no): ").lower()

    if answer in ["yes", "y"]:

        print("Thank you for using the ATM")
        return False

    elif answer in ["no", "n"]:

        return True

    else:

        print("Invalid choice")
        return repeat()