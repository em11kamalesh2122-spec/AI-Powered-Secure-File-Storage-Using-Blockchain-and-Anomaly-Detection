from Crypto.Cipher import AES
import hashlib

KEY = b'PaandiSecureKey!'   # 16 bytes

def encrypt_file(input_file, output_file):

    cipher = AES.new(KEY, AES.MODE_EAX)

    with open(input_file, 'rb') as f:
        data = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(output_file, 'wb') as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)

    print("✅ AES Encryption Successful")


def decrypt_file(encrypted_file, output_file):

    with open(encrypted_file, 'rb') as f:

        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)

    data = cipher.decrypt_and_verify(ciphertext, tag)

    with open(output_file, 'wb') as f:
        f.write(data)

    print("✅ AES Decryption Successful")


def calculate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        while True:

            data = f.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()
