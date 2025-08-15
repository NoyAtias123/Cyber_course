from PIL import Image
import numpy as np

def steganography(code_path: str, img_path: str, new_img_path: str) -> None:
    # Convert the code to a binary string
    with open(code_path, "rb") as f:
        bits = ''.join(format(byte, '08b') for byte in f.read())

    # Open the image
    img = Image.open(img_path)

    # Converts the image to a NumPy array, where each value represents a pixel color
    arr = np.array(img)
    # Turns the list (not one-dimensional) into one long list of all values (one-dimensional)
    flat = arr.flatten()

    # Goes through each bit (0 or 1) of the code
    for i, bit in enumerate(bits):
        # Deletes the last bit (Least Significant Bit) of the number and adds a bit from the code in its place (0 or 1)
        # Changing the last bit changes the color so slightly that the human eye won't notice
        flat[i] = (flat[i] & ~1) | int(bit)

    # Restore the list to its original structure (not one-dimensional)
    arr = flat.reshape(arr.shape)
    # Converts the list of pixels back to an image
    stego_img = Image.fromarray(arr)
    # Saves the image with the hidden code
    stego_img.save(new_img_path)

    print("The malicious image with the code")
    # Displaying the malicious image
    stego_img.show()


if __name__ == "__main__":
    code_path = "H://NOY//אקדמיית המתכנתים//Cyber_course//project_1 - Keylogger//keylogger.py"
    img_path = "H://NOY//אקדמיית המתכנתים//Cyber_course//project_1 - Keylogger//smiley.jpg"
    new_img_path = "H://NOY//אקדמיית המתכנתים//Cyber_course//project_1 - Keylogger//hidden_image.png"
    steganography(code_path, img_path, new_img_path)