import pytest

from core.data_models import User
from db.database import DatabaseManager
from util.enums import InsertStatus


# Create a temporary in-memory database for testing
@pytest.fixture
def db():
    database = DatabaseManager(':memory:')

    # Create tables directly since we're using in-memory db
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
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    database.conn.commit()

    yield database
    database.close()

# Database fixture with a test user already inserted
@pytest.fixture
def db_with_user(db: DatabaseManager):
    _ = db.insert_user('testuser', b'test_hash', b'test_salt')
    user = db.get_user_from_username('testuser')
    return db, user


class TestUserOperations:
    # Test successful user insertion
    def test_insert_user_success(self, db: DatabaseManager) -> None:
        status = db.insert_user('newuser', b'hash123', b'salt123')

        assert status == InsertStatus.SUCCESS

        # Verify user was inserted
        user = db.get_user_from_username('newuser')
        assert user is not None
        assert user.username == 'newuser'
        assert user.master_hash == b'hash123'
        assert user.salt == b'salt123'

    # Test that inserting duplicate username fails
    def test_insert_user_duplicate_username(self, db: DatabaseManager) -> None:
        _ = db.insert_user('duplicate', b'hash1', b'salt1')
        status = db.insert_user('duplicate', b'hash2', b'salt2')

        assert status == InsertStatus.ERROR

    # Test retrieving an existing user
    def test_get_user_from_username_exists(self, db: DatabaseManager) -> None:
        _ = db.insert_user('existinguser', b'hash', b'salt')
        user = db.get_user_from_username('existinguser')

        assert user is not None
        assert isinstance(user, User)
        assert user.username == 'existinguser'
        assert user.master_hash == b'hash'
        assert user.salt == b'salt'

    # Test retrieving a non-existent user
    def test_get_user_from_username_not_exists(self, db: DatabaseManager) -> None:
        user = db.get_user_from_username('nonexistent')

        assert user is None

    # Test successful username update
    def test_update_username_success(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        status = db.update_username(user.id, 'newusername')

        assert status == InsertStatus.SUCCESS

        # Verify the update
        updated_user = db.get_user_from_username('newusername')
        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.username == 'newusername'

    # Test that updating to existing username fails
    def test_update_username_duplicate(self, db: DatabaseManager) -> None:
        _ = db.insert_user('user1', b'hash1', b'salt1')
        _ = db.insert_user('user2', b'hash2', b'salt2')

        user1 = db.get_user_from_username('user1')
        assert user1 is not None
        status = db.update_username(user1.id, 'user2')

        assert status == InsertStatus.ERROR


class TestVaultEntryOperations:
    # Test successful login insertion
    def test_insert_login_success(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        status = db.insert_login(user.id, 'GitHub', 'myusername', b'encrypted_pass')

        assert status == InsertStatus.SUCCESS

        # Verify login was inserted
        logins = db.get_user_logins(user.id)
        assert len(logins) == 1
        assert logins[0].service_name == 'GitHub'
        assert logins[0].username == 'myusername'

    # Test inserting login without username field
    def test_insert_login_without_username(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        status = db.insert_login(user.id, 'API Key', None, b'encrypted_key')

        assert status == InsertStatus.SUCCESS

        logins = db.get_user_logins(user.id)
        assert len(logins) == 1
        assert logins[0].service_name == 'API Key'
        assert logins[0].username is None

    # Test inserting login with invalid user_id fails
    def test_insert_login_invalid_user_id(self, db: DatabaseManager) -> None:
        status = db.insert_login(999, 'Service', 'user', b'pass')

        assert status == InsertStatus.ERROR

    # Test retrieving multiple logins for a user
    def test_get_user_logins_multiple(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        _ = db.insert_login(user.id, 'GitHub', 'user1', b'pass1')
        _ = db.insert_login(user.id, 'Gmail', 'user2', b'pass2')
        _ = db.insert_login(user.id, 'Twitter', 'user3', b'pass3')

        logins = db.get_user_logins(user.id)

        assert len(logins) == 3
        service_names = [login.service_name for login in logins]
        assert 'GitHub' in service_names
        assert 'Gmail' in service_names
        assert 'Twitter' in service_names

    # Test retrieving logins when user has none
    def test_get_user_logins_empty(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        logins = db.get_user_logins(user.id)

        assert logins == [] or logins == [None]  # Depends on your implementation

    # Test retrieving logins by service name
    def test_get_logins_from_name(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        _ = db.insert_login(user.id, 'Gmail', 'personal@gmail.com', b'pass1')
        _ = db.insert_login(user.id, 'Gmail', 'work@gmail.com', b'pass2')
        _ = db.insert_login(user.id, 'GitHub', 'user', b'pass3')

        gmail_logins = db.get_logins_from_name(user.id, 'Gmail')

        assert len(gmail_logins) == 2
        usernames = [login.username for login in gmail_logins]
        assert 'personal@gmail.com' in usernames
        assert 'work@gmail.com' in usernames

    # Test retrieving logins for non-existent service
    def test_get_logins_from_name_not_found(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        logins = db.get_logins_from_name(user.id, 'NonExistent')

        assert logins == [] or logins == [None]  # Depends on your implementation

    # Test that multiple users have isolated vaults
    def test_multiple_users_isolated_vaults(self, db: DatabaseManager) -> None:
        _ = db.insert_user('user1', b'hash1', b'salt1')
        _ = db.insert_user('user2', b'hash2', b'salt2')

        user1 = db.get_user_from_username('user1')
        user2 = db.get_user_from_username('user2')

        assert user1 is not None
        assert user2 is not None

        _ = db.insert_login(user1.id, 'Service1', 'user1account', b'pass1')
        _ = db.insert_login(user2.id, 'Service2', 'user2account', b'pass2')

        user1_logins = db.get_user_logins(user1.id)
        user2_logins = db.get_user_logins(user2.id)

        assert len(user1_logins) == 1
        assert len(user2_logins) == 1
        assert user1_logins[0].service_name == 'Service1'
        assert user2_logins[0].service_name == 'Service2'


class TestDatabaseUtilities:
    # Test clearing the database
    def test_clear_database(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        _ = db.insert_login(user.id, 'GitHub', 'user', b'pass')

        db.clear_database()

        # Verify database is empty
        all_users = db.cur.execute('SELECT * FROM users').fetchall()
        all_logins = db.cur.execute('SELECT * FROM vault_entries').fetchall()

        assert len(all_users) == 0
        assert len(all_logins) == 0

    # Test that foreign key constraints are enforced
    def test_foreign_key_constraint(self, db: DatabaseManager) -> None:
        # Try to insert a login without a valid user_id
        status = db.insert_login(999, 'Service', 'user', b'pass')

        assert status == InsertStatus.ERROR

    # Test that data persists after operations
    def test_database_persistence(self, db_with_user: tuple[DatabaseManager, User]) -> None:
        db, user = db_with_user
        _ = db.insert_login(user.id, 'Service', 'user', b'pass')

        # Retrieve and verify
        logins = db.get_user_logins(user.id)
        assert len(logins) == 1

        # Insert another and verify both exist
        _ = db.insert_login(user.id, 'Service2', 'user2', b'pass2')
        logins = db.get_user_logins(user.id)
        assert len(logins) == 2
