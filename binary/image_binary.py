def image_binary():
    with open(r"C:\Users\Admin\python-projects\Sample-Test\binary\rajini.jpeg", "rb") as f:
        binary_data = f.read()

    with open("image.bin", "wb") as f:
        f.write(binary_data)

    print("Image converted to binary successfully!")

image_binary()