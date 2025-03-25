from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from os import urandom
import base64

# Function to encrypt a single latitude or longitude independently
def encrypt_value(value, key):
    # Ensure the value is padded to be a multiple of the AES block size (128 bits or 16 bytes)
    #the block size is always 128 bits (16 bytes)
    padder = padding.PKCS7(128).padder()
    #PKCS7 is a padding scheme used to make the length of the data a multiple of the AES block size (128 bits, or 16 bytes)
    padded_data = padder.update(str(value).encode()) + padder.finalize()

    #padder.update() method adds the actual padding to the data
    #The padder.finalize() method finalizes the padding, ensuring the padding is added correctly.
    
    # Generate a random IV (Initialization Vector) for each encryption operation
    iv = urandom(16)  # AES block size is 16 bytes
    
    # Create an AES cipher object with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Encrypt the padded data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return the IV and encrypted data, encoded in base64 for easy storage or transmission
    #Since encryption results in binary data, Base64 encoding makes the data easier to transmit or store in a text-based format.
    #return base64.b64encode(iv + encrypted_data).decode('utf-8')
    return encrypted_data.hex(),iv.hex()

# Function to decrypt the encrypted data
def decrypt_value(encrypted_data_hex, iv_hex, key):
    # Convert the hexadecimal strings back to bytes
    encrypted_data = bytes.fromhex(encrypted_data_hex)
    iv = bytes.fromhex(iv_hex)

    # Create an AES cipher object with CBC mode using the extracted IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Decrypt the data
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Unpad the decrypted data to get the original value
    unpadder = padding.PKCS7(128).unpadder()
    value = unpadder.update(decrypted_data) + unpadder.finalize()
    
    # Decode the decrypted value and return as float (assuming the original data was numeric)
    return float(value.decode())

