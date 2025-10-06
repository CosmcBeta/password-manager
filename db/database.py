import logging
import os
import sqlite3

from core.enums import InsertStatus

logger: logging.Logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self) -> None:
        exists = os.path.exists('data/vault.db')
        self.conn: sqlite3.Connection = sqlite3.connect('data/vault.db')
        _ = self.conn.execute('PRAGMA foreign_keys = ON')
        self.cur: sqlite3.Cursor = self.conn.cursor()
        if not exists:
            self.create_database()

    def create_database(self):
        with open('db/schema.sql', 'r') as f:
            schema = f.read()
        _ = self.cur.executescript(schema)
        self.conn.commit()

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

    def get_user(self, username: str):
        try:
            _ = self.cur.execute('SELECT * FROM users WHERE username = (?)', (username,))
            logger.info(f'Retrieved the user \'{username}\' successfully')
            return self.cur.fetchone()

        except sqlite3.InterfaceError as e:
            logger.error(f'Error retrieving the user \'{username}\': {e}')
            return None

    def get_login(self, name: str):
        try:
            _ = self.cur.execute('SELECT * FROM vault_entries WHERE service_name = (?)', (name,))
            logger.info(f'Retrieved all entries where name is \'{name}\'')
            return self.cur.fetchall()
        except sqlite3.IntegrityError as e:
            logger.error(f'Error retrieving entries with name \'{name}\': {e}')
            return None

    def get_user_logins(self, user_id: int):
        try:
            _ = self.cur.execute('SELECT * FROM vault_entries WHERE user_id = (?)', (user_id,))
            logger.info(f'Retrieved all entries from user is \'{user_id}\'')
            return self.cur.fetchall()
        except sqlite3.IntegrityError as e:
            logger.error(f'Error retrieving entries from user \'{user_id}\': {e}')
            return None
