import os

import pytest
from cryptography.fernet import InvalidToken

from core.encryption import EncryptionManager


@pytest.fixture
def encryption():
    return EncryptionManager()

def test_encrypt_and_decrypt_password(encryption: EncryptionManager):
    key = encryption.derive_key("mypassword", os.urandom(16))
    plaintext = "super_secret_123"

    encrypted = encryption.encrypt_password(key, plaintext)
    assert isinstance(encrypted, bytes)
    assert plaintext.encode() not in encrypted  # not stored as plaintext

    decrypted = encryption.decrypt_password(key, encrypted)
    assert decrypted.decode() == plaintext

def test_decrypt_with_wrong_key(encryption: EncryptionManager):
    key1 = encryption.derive_key("password1", os.urandom(16))
    key2 = encryption.derive_key("password2", os.urandom(16))
    plaintext = "secret"

    encrypted = encryption.encrypt_password(key1, plaintext)

    with pytest.raises(InvalidToken):
        _ = encryption.decrypt_password(key2, encrypted)

def test_derive_key_consistency(encryption: EncryptionManager):
    salt = os.urandom(16)
    key1 = encryption.derive_key("samepassword", salt)
    key2 = encryption.derive_key("samepassword", salt)
    assert key1 == key2  # deterministic

    different_salt = os.urandom(16)
    key3 = encryption.derive_key("samepassword", different_salt)
    assert key1 != key3  # salt affects output

def test_hash_and_verify_master_password(encryption: EncryptionManager):
    password = "masterpass123"
    salt, stored_hash = encryption.hash_master_password(password)

    assert isinstance(stored_hash, bytes)
    assert isinstance(salt, bytes)
    assert encryption.vertify_master_password(password, salt, stored_hash)
    assert not encryption.vertify_master_password("wrongpass", salt, stored_hash)
