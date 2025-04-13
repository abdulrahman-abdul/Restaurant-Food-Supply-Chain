from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64
import zlib
from Crypto.Random import get_random_bytes


def generate_random_aes_key(key_size=16):  # AES key size in bytes (128-bit)
    return get_random_bytes(key_size)

def generate_rsa_keys(key_size=4096):  # Keep key size reasonable for security
    key = RSA.generate(key_size)
    private_key = key.export_key()
    with open("private_key.pem", "wb") as private_file:
        private_file.write(private_key)

    public_key = key.publickey().export_key()
    with open("public_key.pem", "wb") as public_file:
        public_file.write(public_key)


def load_rsa_private_key():
    with open("private_key.pem", "rb") as private_file:
        private_key = RSA.import_key(private_file.read())
    return private_key


def load_rsa_public_key():
    with open("public_key.pem", "rb") as public_file:
        public_key = RSA.import_key(public_file.read())
    return public_key


def compress_data(data: str) -> bytes:
    return zlib.compress(data.encode(), level=zlib.Z_BEST_COMPRESSION)


def decompress_data(data: bytes) -> str:
    return zlib.decompress(data).decode()


def encrypt_message(message: str) -> str:
    # Compress the message (optional)
    compressed_message = compress_data(message)

    # Generate a random AES key (128-bit)
    aes_key = get_random_bytes(16)  # 128 bits = 16 bytes

    # Encrypt the compressed message using AES in ECB mode (no IV)
    cipher_aes = AES.new(aes_key, AES.MODE_ECB)
    padded_message = compressed_message + b' ' * (16 - len(compressed_message) % 16)
    ciphertext = cipher_aes.encrypt(padded_message)

    # Encrypt the AES key with RSA
    public_key = load_rsa_public_key()
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    # Combine the encrypted AES key with the ciphertext and encode it
    encrypted_data = base64.urlsafe_b64encode(encrypted_aes_key + ciphertext).decode()
    return encrypted_data


def decrypt_message(encrypted_message: str) -> str:
    private_key = load_rsa_private_key()
    cipher_rsa = PKCS1_OAEP.new(private_key)

    # Decode the base64-encoded message
    encrypted_data = base64.urlsafe_b64decode(encrypted_message)

    # Extract the encrypted AES key and ciphertext
    encrypted_aes_key = encrypted_data[:private_key.size_in_bytes()]
    ciphertext = encrypted_data[private_key.size_in_bytes():]

    # Decrypt the AES key using RSA
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    # Decrypt the ciphertext using the AES key (ECB mode)
    cipher_aes = AES.new(aes_key, AES.MODE_ECB)
    padded_message = cipher_aes.decrypt(ciphertext)
    compressed_message = padded_message.rstrip(b' ')

    # Decompress and return the original message
    return decompress_data(compressed_message)


# Example usage
if __name__ == "__main__":
    # Generate RSA keys (only once)
    generate_rsa_keys()

    # Example message
    message = "This is a blockchain message with a significant amount of data to compress and encrypt."

    # Encrypt the message
    encrypted_message = encrypt_message(message)
    print("Encrypted Message:", encrypted_message)

    # Decrypt the message
    decrypted_message = decrypt_message(encrypted_message)
    print("Decrypted Message:", decrypted_message)
