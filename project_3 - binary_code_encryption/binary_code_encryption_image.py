import numpy as np
from PIL import Image

def input_image():
    img_path = input("Enter image path:")
    try:
        img = Image.open(img_path)
        return img
    except:
        print("There is a problem with the file (cannot open or does not exist). Try again")
        return input_image()


def image_Encryption(encrypted_array: np.ndarray) -> None:
    encrypted_img = Image.fromarray(encrypted_array)
    encrypted_img.save("encoded_image.png")
    encrypted_img.show()


def image_Decoding(xor_key: int, encrypted_array: np.ndarray) -> None:
    decrypted_array = encrypted_array ^ xor_key
    decrypted_img = Image.fromarray(decrypted_array)
    decrypted_img.save("decrypted_image.png")
    decrypted_img.show()


def change_image_according_user(xor_key: int, encrypted_array: np.ndarray) -> None:
    action = input("Enter what type of operation to perform: encrypt or decrypt:")
    if action == "encrypt":
        image_Encryption(encrypted_array)
    elif action == "decrypt":
        image_Decoding(xor_key, encrypted_array)
    else:
        print("A wrong action entered, try again!")
        return change_image_according_user(xor_key, encrypted_array)



if __name__ == "__main__":
    img = input_image()
    img_array = np.array(img)
    key = int(input("Enter a number with which you want to encrypt the image with xor:"))
    encrypted_array = img_array ^ key
    change_image_according_user(key, encrypted_array)