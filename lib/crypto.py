import os
import base64
from Crypto.Cipher import AES

def _get_key():
    key_hex = os.getenv("TOKEN_ENCRYPTION_KEY")
    return base64.b16decode(key_hex, casefold=True)

def encrypt(plaintext: str) -> str:
    key = _get_key()
    iv = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    return base64.b64encode(iv + tag + ciphertext).decode('utf-8')

def decrypt(token_b64: str) -> str:
    data = base64.b64decode(token_b64)
    iv, tag, ciphertext = data[:12], data[12:28], data[28:]
    key = _get_key()
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    cipher.update(b"")
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')
