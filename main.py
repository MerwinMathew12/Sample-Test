from calc import add,sub,mul,div
def calculator(num1, num2, opr):
    if opr == "+" or opr == "add":
        return add(num1, num2)
    elif opr == "-" or opr == "sub":
        return sub(num1, num2)
    elif opr == "*" or opr == "mul":
        return mul(num1, num2)
    elif opr == "/" or opr == "div":
        return div(num1, num2)

num1 = int(input("Enter 1st Number:"))
num2 = int(input("Enter 2nd Number:"))
opr = input("Enter OPERATION:")

if __name__ == "__main__":
    print(calculator(num1, num2, opr))