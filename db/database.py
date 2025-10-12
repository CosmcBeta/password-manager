import logging
import os
import sqlite3

from core.data_models import User, VaultEntry
from util.enums import InsertStatus

logger: logging.Logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'data/vault.db') -> None:
        exists = os.path.exists(db_path) if db_path != ':memory:' else False

        self.conn: sqlite3.Connection = sqlite3.connect(db_path)
        _ = self.conn.execute('PRAGMA foreign_keys = ON')
        self.cur: sqlite3.Cursor = self.conn.cursor()

        if not exists:
            self.create_database()

    # Closes the database connection
    def close(self) -> None:
        self.conn.close()

    # Creates the database
    def create_database(self):
        with open('db/schema.sql', 'r') as f:
            schema = f.read()
        _ = self.cur.executescript(schema)
        self.conn.commit()

    # Clears database for test files
    def clear_database(self):
        _ = self.cur.execute('DELETE FROM vault_entries;')
        _ = self.cur.execute('DELETE FROM users;')
        self.conn.commit()

        # Reset autoincrement counters
        _ = self.cur.execute('DELETE FROM sqlite_sequence;')
        self.conn.commit()

    # Adds user
    def insert_user(self, username: str, master_hash: bytes, salt: bytes) -> InsertStatus:
        try:
            _ = self.cur.execute('INSERT INTO users (username, master_hash, salt) \
                                VALUES (?, ?, ?)', (username, master_hash, salt))
            self.conn.commit()
            logger.info(f'Inserted user \'{username}\' successfully')

            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            logger.error(f'Error inserting user \'{username}\': {e}')
            self.conn.rollback()

            return InsertStatus.ERROR

    # Adds login
    def insert_login(self, user_id: int, name: str, username: str | None, password: bytes) -> InsertStatus:
        try:
            _ = self.cur.execute('INSERT INTO vault_entries (user_id, service_name, username, password_encrypted) \
                                VALUES (?, ?, ?, ?)', (user_id, name, username, password))
            self.conn.commit()
            logger.info(f'Inserted login \'{name}\' successfully')

            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            logger.error(f'Error inserting login \'{name}\': {e}')
            self.conn.rollback()

            return InsertStatus.ERROR

    # Returns user given username
    def get_user_from_username(self, username: str):
        try:
            _ = self.cur.execute('SELECT * FROM users WHERE username = (?)', (username,))
            logger.info(f'Retrieved the user \'{username}\' successfully')
            row: tuple[int, str, bytes, bytes] | None = self.cur.fetchone()
            if row:
                return User(*row)
            return None

        except sqlite3.InterfaceError as e:
            logger.error(f'Error retrieving the user \'{username}\': {e}')
            return None

    # Returns a list of all entries from a given name and with the given user
    def get_logins_from_name(self, user_id: int, name: str) -> list[VaultEntry]:
        try:
            _ = self.cur.execute('SELECT * FROM vault_entries WHERE user_id = ? AND service_name = ?', (user_id, name))
            logger.info(f'Retrieved all entries where name is \'{name}\'')
            rows: list[tuple[int, int, str, str, bytes]] = self.cur.fetchall()
            return [VaultEntry(*row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f'Error retrieving entries with user \'{user_id}\' and name \'{name}\': {e}')
            return []

    # Returns a list of all entries assigned to the user
    def get_user_logins(self, user_id: int) -> list[VaultEntry]:
        try:
            _ = self.cur.execute('SELECT * FROM vault_entries WHERE user_id = ?', (user_id,))
            logger.info(f'Retrieved all entries from user is \'{user_id}\'')
            rows: list[tuple[int, int, str, str, bytes]] = self.cur.fetchall()
            return [VaultEntry(*row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f'Error retrieving entries from user \'{user_id}\': {e}')
            return []

    # Updates username for a user
    def update_username(self, user_id: int, new_username: str) -> InsertStatus:
        try:
            _ = self.cur.execute('UPDATE users SET username = ? \
                                WHERE id = ?', (new_username, user_id))
            self.conn.commit()
            logger.info(f'Updated username to \'{new_username}\' for user_id {user_id}')
            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            logger.error(f'Error updating username for user_id {user_id}: {e}')
            self.conn.rollback()
            return InsertStatus.ERROR
