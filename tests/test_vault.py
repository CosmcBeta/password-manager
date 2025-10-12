from unittest.mock import patch

import pytest

from core.data_models import User
from core.vault import Vault
from db.database import DatabaseManager
from util.enums import InsertStatus, RemoveStatus


# Create a temporary in-memory database for testing
@pytest.fixture
def db():
    database = DatabaseManager(':memory:')

    _ = database.cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        master_hash BLOB NOT NULL,
        salt BLOB NOT NULL
    )''')
    _ = database.cur.execute('''CREATE TABLE IF NOT EXISTS vault_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        username TEXT,
        password_encrypted BLOB NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )''')
    database.conn.commit()

    yield database
    database.close()

# Create a Vault instance with test database
@pytest.fixture
def vault(db: DatabaseManager):
    return Vault(db)

# Create a test user and return User object
@pytest.fixture
def test_user(vault: Vault):
    username = 'testuser'
    password = 'TestPassword123!@#'

    _ = vault.create_user(username, password)
    user = vault.database.get_user_from_username(username)

    return user, password

# Test successful user creation
class TestUserCreation:
    def test_create_user_success(self, vault: Vault) -> None:
        status = vault.create_user('newuser', 'SecurePass123!@#')

        assert status == InsertStatus.SUCCESS

        user = vault.database.get_user_from_username('newuser')
        assert user is not None
        assert user.username == 'newuser'
        assert len(user.master_hash) == 32
        assert len(user.salt) == 16

    # Test creating duplicate user fails
    def test_create_user_duplicate(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        status = vault.create_user(user.username, 'DifferentPass123!@#')

        assert status == InsertStatus.ERROR

    # Test verifying correct master password
    def test_check_master_password_correct(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        result = vault.check_master_password(user, password)

        assert result is True

    # Test verifying incorrect master password
    def test_check_master_password_incorrect(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        result = vault.check_master_password(user, 'WrongPassword123!@#')

        assert result is False


class TestLoginManagement:
    # Test adding a login successfully
    def test_add_login_success(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        status = vault.add_login(user, 'GitHub', 'myusername', 'github_pass123')

        assert status == InsertStatus.SUCCESS

        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 1
        assert logins[0].service_name == 'GitHub'
        assert logins[0].username == 'myusername'

    # Test adding a login without username
    def test_add_login_without_username(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        status = vault.add_login(user, 'API Key', None, 'secret_key')

        assert status == InsertStatus.SUCCESS

        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 1
        assert logins[0].username is None

    # Test adding multiple logins
    def test_add_multiple_logins(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user

        _ = vault.add_login(user, 'GitHub', 'user1', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'user2', 'pass2')
        _ = vault.add_login(user, 'Twitter', 'user3', 'pass3')

        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 3

    # Test that passwords are encrypted when stored
    def test_add_login_encrypts_password(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        plain_password = 'my_secret_password'

        _ = vault.add_login(user, 'Service', 'username', plain_password)

        logins = vault.database.get_user_logins(user.id)
        # Encrypted password should not equal plain password
        assert logins[0].password_encrypted != plain_password.encode()

        # But should decrypt back to original
        decrypted = vault.encryption.decrypt_password(user.master_hash, logins[0].password_encrypted)
        assert decrypted.decode() == plain_password


class TestListLogins:
    # Test listing logins when user has none
    def test_list_logins_empty(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        vault.list_logins(user)

        captured = capsys.readouterr()
        assert 'You have no logins' in captured.out

    # Test listing a single login
    def test_list_logins_single(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'myuser', 'mypass')

        vault.list_logins(user)

        captured = capsys.readouterr()
        assert 'GitHub' in captured.out
        assert 'myuser' in captured.out
        assert 'mypass' in captured.out

    # Test listing multiple logins
    def test_list_logins_multiple(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'user1', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'user2', 'pass2')

        vault.list_logins(user)

        captured = capsys.readouterr()
        assert 'GitHub' in captured.out
        assert 'Gmail' in captured.out
        assert 'user1' in captured.out
        assert 'user2' in captured.out

    # Test listing login without username shows N/A
    def test_list_logins_without_username(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        vault.add_login(user, 'API', None, 'secret')

        vault.list_logins(user)

        captured = capsys.readouterr()
        assert 'N/A' in captured.out


class TestRemoveLogin:
    # Test removing a single login with confirmation
    @patch('builtins.input', return_value='yes')
    def test_remove_login_single_confirm(self, mock_input, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'user', 'pass')

        status = vault.remove_login(user, 'GitHub')

        assert status == RemoveStatus.SUCCESS
        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 0

    # Test cancelling removal of a single login
    @patch('builtins.input', return_value='no')
    def test_remove_login_single_cancel(self, mock_input, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'user', 'pass')

        status = vault.remove_login(user, 'GitHub')

        assert status == RemoveStatus.ERROR
        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 1

    # Test removing non-existent login
    def test_remove_login_not_found(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        status = vault.remove_login(user, 'NonExistent')

        assert status == RemoveStatus.ERROR
        captured = capsys.readouterr()
        assert 'No logins found' in captured.out

    # Test removing first login when multiple exist
    @patch('builtins.input', side_effect=['1', 'yes'])
    def test_remove_login_multiple_select_first(self, mock_input, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'Gmail', 'personal@gmail.com', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'work@gmail.com', 'pass2')

        status = vault.remove_login(user, 'Gmail')

        assert status == RemoveStatus.SUCCESS
        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 1

    # Test cancelling when selecting from multiple logins
    @patch('builtins.input', return_value='cancel')
    def test_remove_login_multiple_cancel(self, mock_input, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'Gmail', 'personal@gmail.com', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'work@gmail.com', 'pass2')

        status = vault.remove_login(user, 'Gmail')

        assert status == RemoveStatus.ERROR
        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 2


class TestGetLoginInformation:
    # Test getting info for a single login
    def test_get_login_info_single(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'myuser', 'mypass')

        vault.get_login_information(user, 'GitHub')

        captured = capsys.readouterr()
        assert 'GitHub' in captured.out
        assert 'myuser' in captured.out
        assert 'mypass' in captured.out

    # Test getting info for non-existent login
    def test_get_login_info_not_found(self, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        vault.get_login_information(user, 'NonExistent')

        captured = capsys.readouterr()
        assert 'No logins found' in captured.out

    # Test selecting from multiple logins
    @patch('builtins.input', return_value='1')
    def test_get_login_info_multiple_select(self, mock_input, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'Gmail', 'personal@gmail.com', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'work@gmail.com', 'pass2')

        vault.get_login_information(user, 'Gmail')

        captured = capsys.readouterr()
        assert 'Gmail' in captured.out
        assert 'personal@gmail.com' in captured.out

    # Test cancelling when viewing multiple logins
    @patch('builtins.input', return_value='cancel')
    def test_get_login_info_multiple_cancel(self, mock_input, vault: Vault, test_user: tuple[User, str], capsys: pytest.CaptureFixture[str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'Gmail', 'personal@gmail.com', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'work@gmail.com', 'pass2')

        vault.get_login_information(user, 'Gmail')

        captured = capsys.readouterr()
        assert 'Cancelled' in captured.out


class TestRemoveUser:
    # Test removing a user
    def test_remove_user_success(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'user', 'pass')

        status = vault.remove_user(user)

        assert status == RemoveStatus.SUCCESS

        # Verify user is deleted
        deleted_user = vault.database.get_user_from_username(user.username)
        assert deleted_user is None

        # Verify logins are also deleted (cascade)
        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 0

    # Test removing user with multiple logins cascades
    def test_remove_user_with_multiple_logins(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        _ = vault.add_login(user, 'GitHub', 'user1', 'pass1')
        _ = vault.add_login(user, 'Gmail', 'user2', 'pass2')
        _ = vault.add_login(user, 'Twitter', 'user3', 'pass3')

        status = vault.remove_user(user)

        assert status == RemoveStatus.SUCCESS
        logins = vault.database.get_user_logins(user.id)
        assert len(logins) == 0


class TestEncryptionIntegrity:
    # Test that encrypted passwords decrypt correctly
    def test_password_decryption_integrity(self, vault: Vault, test_user: tuple[User, str]) -> None:
        user, password = test_user
        original_password = 'TestPassword123!@#$%'

        _ = vault.add_login(user, 'Service', 'username', original_password)

        logins = vault.database.get_user_logins(user.id)
        encrypted = logins[0].password_encrypted

        decrypted = vault.encryption.decrypt_password(user.master_hash, encrypted)

        assert decrypted.decode() == original_password

    # Test that same password encrypts differently for different users
    def test_different_users_different_encryption(self, vault: Vault) -> None:
        # Create two users
        _ = vault.create_user('user1', 'MasterPass1!@#')
        _ = vault.create_user('user2', 'MasterPass2!@#')

        user1 = vault.database.get_user_from_username('user1')
        user2 = vault.database.get_user_from_username('user2')

        assert user1 is not None
        assert user2 is not None

        same_password = 'SharedPassword123'

        _ = vault.add_login(user1, 'Service', 'user1', same_password)
        _ = vault.add_login(user2, 'Service', 'user2', same_password)

        user1_logins = vault.database.get_user_logins(user1.id)
        user2_logins = vault.database.get_user_logins(user2.id)

        # Encrypted passwords should be different
        assert user1_logins[0].password_encrypted != user2_logins[0].password_encrypted

        # But both should decrypt to the same original password
        decrypted1 = vault.encryption.decrypt_password(user1.master_hash, user1_logins[0].password_encrypted)
        decrypted2 = vault.encryption.decrypt_password(user2.master_hash, user2_logins[0].password_encrypted)

        assert decrypted1.decode() == same_password
        assert decrypted2.decode() == same_password
