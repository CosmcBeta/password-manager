import logging
import os
import sqlite3

from core.enums import InsertStatus
from core.models import User, VaultEntry

logger: logging.Logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self) -> None:
        exists = os.path.exists('data/vault.db')
        self.conn: sqlite3.Connection = sqlite3.connect('data/vault.db')
        _ = self.conn.execute('PRAGMA foreign_keys = ON')
        self.cur: sqlite3.Cursor = self.conn.cursor()
        if not exists:
            self.create_database()

    # Creates the database
    def create_database(self):
        with open('db/schema.sql', 'r') as f:
            schema = f.read()
        _ = self.cur.executescript(schema)
        self.conn.commit()

    # Adds user
    def insert_user(self, username: str, master_hash: str, salt: str) -> InsertStatus:
        try:
            _ = self.cur.execute('INSERT INTO users (username, master_hash, salt) \
                                VALUES (?, ?, ?)', (username, master_hash, salt))
            self.conn.commit()
            logger.info(f'Inserted user \'{username}\' successfully')

            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            logger.error(f'Error inserting user \'{username}\': {e}')
            self.conn.rollback()

            return InsertStatus.OTHER_ERROR

    # Adds login
    def insert_login(self, user_id: int, name: str, username: str | None, password: str) -> InsertStatus:
        try:
            _ = self.cur.execute('INSERT INTO vault_entries (user_id, service_name, username, password_encrypted) \
                                VALUES (?, ?, ?, ?)', (user_id, name, username, password))
            self.conn.commit()
            logger.info(f'Inserted login \'{name}\' successfully')

            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            logger.error(f'Error inserting login \'{name}\': {e}')
            self.conn.rollback()

            return InsertStatus.OTHER_ERROR

    # Returns user given username
    def get_user_from_username(self, username: str):
        try:
            _ = self.cur.execute('SELECT * FROM users WHERE username = (?)', (username,))
            logger.info(f'Retrieved the user \'{username}\' successfully')
            row: tuple[int, str, str, str] | None = self.cur.fetchone()
            if row:
                return User(*row)
            return None

        except sqlite3.InterfaceError as e:
            logger.error(f'Error retrieving the user \'{username}\': {e}')
            return None

    # Returns a list of all entries from a given name and with the given user
    def get_logins_from_name(self, user_id: int, name: str) -> list[VaultEntry] | list[None]:
        try:
            _ = self.cur.execute('SELECT * FROM vault_entries WHERE user_id = ? AND service_name = ?', (user_id, name))
            logger.info(f'Retrieved all entries where name is \'{name}\'')
            rows: list[tuple[int, int, str, str, str]] = self.cur.fetchall()
            if rows:
                return [VaultEntry(*row) for row in rows]
            else:
                return [None]

        except sqlite3.IntegrityError as e:
            logger.error(f'Error retrieving entries with user \'{user_id}\' and name \'{name}\': {e}')
            return [None]

    # Returns a list of all entries assigned to the user
    def get_user_logins(self, user_id: int) -> list[VaultEntry] | list[None]:
        try:
            _ = self.cur.execute('SELECT * FROM vault_entries WHERE user_id = ?', (user_id,))
            logger.info(f'Retrieved all entries from user is \'{user_id}\'')
            rows: list[tuple[int, int, str, str, str]] = self.cur.fetchall()
            if rows:
                return [VaultEntry(*row) for row in rows]
            else:
                return [None]
        except sqlite3.IntegrityError as e:
            logger.error(f'Error retrieving entries from user \'{user_id}\': {e}')
            return [None]
