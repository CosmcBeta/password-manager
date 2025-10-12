import pytest

from core.encryption import EncryptionManager


# Create an EncryptionManager instance for testing
@pytest.fixture
def encryption() -> EncryptionManager:
    return EncryptionManager()

# Test that hash_master_password returns a salt and hash
def test_hash_master_password_returns_salt_and_hash(encryption: EncryptionManager) -> None:
    password = 'test_password_123'
    salt, hash = encryption.hash_master_password(password)

    assert isinstance(salt, bytes)
    assert isinstance(hash, bytes)
    assert len(salt) == 16
    assert len(hash) == 32

# Test that each call generates a unique salt
def test_hash_master_password_generates_unique_salts(encryption: EncryptionManager) -> None:
    password = 'same_password'
    salt1, hash1 = encryption.hash_master_password(password)
    salt2, hash2 = encryption.hash_master_password(password)

    assert salt1 != salt2
    assert hash1 != hash2

# Test verification with correct password
def test_verify_master_password_correct(encryption: EncryptionManager) -> None:
    password = 'correct_password'
    salt, stored_hash = encryption.hash_master_password(password)

    result = encryption.vertify_master_password(password, salt, stored_hash)

    assert result is True

# Test verification with incorrect password
def test_verify_master_password_incorrect(encryption: EncryptionManager) -> None:
    password = 'correct_password'
    salt, stored_hash = encryption.hash_master_password(password)

    result = encryption.vertify_master_password('wrong_password', salt, stored_hash)

    assert result is False

# Test that derive_key produces consistent results
def test_derive_key_consistent(encryption: EncryptionManager) -> None:
    password = 'test_password'
    salt = b'sixteen_byte_sal'

    key1 = encryption.derive_key(password, salt)
    key2 = encryption.derive_key(password, salt)

    assert key1 == key2
    assert len(key1) == 32

# Test that different salts produce different keys
def test_derive_key_different_salts(encryption: EncryptionManager) -> None:
    password = 'test_password'
    salt1 = b'sixteen_byte_sa1'
    salt2 = b'sixteen_byte_sa2'

    key1 = encryption.derive_key(password, salt1)
    key2 = encryption.derive_key(password, salt2)

    assert key1 != key2

# Test encrypting and decrypting a password
def test_encrypt_decrypt_password(encryption: EncryptionManager) -> None:
    password = 'my_secret_password'
    salt, key = encryption.hash_master_password('master_password')

    encrypted = encryption.encrypt_password(key, password)
    decrypted = encryption.decrypt_password(key, encrypted)

    assert isinstance(encrypted, bytes)
    assert decrypted.decode() == password

# Test that different keys produce different encrypted results
def test_encrypt_password_different_keys(encryption: EncryptionManager) -> None:
    password = 'same_password'
    salt1, key1 = encryption.hash_master_password('master1')
    salt2, key2 = encryption.hash_master_password('master2')

    encrypted1 = encryption.encrypt_password(key1, password)
    encrypted2 = encryption.encrypt_password(key2, password)

    assert encrypted1 != encrypted2

# Test that decrypting with wrong key raises an error
def test_decrypt_with_wrong_key_raises_error(encryption: EncryptionManager) -> None:
    password = 'secret_password'
    salt1, key1 = encryption.hash_master_password('master1')
    salt2, key2 = encryption.hash_master_password('master2')

    encrypted = encryption.encrypt_password(key1, password)

    with pytest.raises(Exception):
        _ = encryption.decrypt_password(key2, encrypted)

# Test encrypting an empty string
def test_encrypt_empty_string(encryption: EncryptionManager) -> None:
    password = ''
    salt, key = encryption.hash_master_password('master_password')

    encrypted = encryption.encrypt_password(key, password)
    decrypted = encryption.decrypt_password(key, encrypted)

    assert decrypted.decode() == password

# Test encrypting password with special characters
def test_encrypt_special_characters(encryption: EncryptionManager) -> None:
    password = 'p@ssw0rd!#$%^&*()'
    salt, key = encryption.hash_master_password('master_password')

    encrypted = encryption.encrypt_password(key, password)
    decrypted = encryption.decrypt_password(key, encrypted)

    assert decrypted.decode() == password

# Test verification with empty password
def test_verify_with_empty_password(encryption: EncryptionManager) -> None:
    password = ''
    salt, stored_hash = encryption.hash_master_password(password)

    result = encryption.vertify_master_password(password, salt, stored_hash)

    assert result is True
