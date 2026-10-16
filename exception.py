# try:
#     a=9
#     b=9
#     print(a+b)
# except exception as e:
#     print ("Error:", e)
# else: 
#     print("No Error, Numbers added Successfully")
# finally:
#     print("Execution Successful")

for i in range(1,11):
    try:
        if i == 3 or i == 5:
            raise Exception("Number (i) is not allowed")
        print(i)
    except Exception as e:
        print({"message": str(e), "status_code": 400})