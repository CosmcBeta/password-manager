import base64
import os

from cryptography.exceptions import InvalidKey
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class EncryptionManager:
    def __init__(self) -> None:
        pass

    # Returns the encrypted password from the key given which should be the master_hash of the user
    def encrypt_password(self, key: bytes, password: str) -> bytes:
        key_b64 = base64.urlsafe_b64encode(key)
        f = Fernet(key_b64)
        return f.encrypt(password.encode())

    # Returns the decrypted password given the key
    def decrypt_password(self, key: bytes, encrypted_password: bytes) -> bytes:
        key_b64 = base64.urlsafe_b64encode(key)
        f = Fernet(key_b64)
        return f.decrypt(encrypted_password.decode())

    # Returns just the key/hash for the password and salt given
    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1
        )
        return kdf.derive(password.encode())

    # Returns the salt and key/hash of the password given
    def hash_master_password(self, password: str) -> tuple[bytes, bytes]:
        salt = os.urandom(16)
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1
        )
        hash = kdf.derive(password.encode())
        return salt, hash

    # Vertifies if the given password matches the stored hash/key
    def vertify_master_password(self, password: str, salt: bytes, stored_hash: bytes) -> bool:
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1
        )
        try:
            kdf.verify(password.encode(), stored_hash)
            return True
        except InvalidKey:
            return False
