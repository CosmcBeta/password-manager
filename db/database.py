import os
import sqlite3
import logging

from core.enums import InsertStatus

class DatabaseManager:
    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
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
            _ = self.conn.execute('INSERT INTO users (username, master_hash, salt) \
                                VALUES (?, ?, ?)', (username, master_hash, salt))
            self.conn.commit()
            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            print(f'Error adding user: {e}')
            self.conn.rollback()
            return InsertStatus.OTHER_ERROR

    def insert_login(self, user_id: int, name: str, username: str | None, password: str) -> InsertStatus:
        try:
            _ = self.conn.execute('INSERT INTO vault_entries (user_id, service_name, username, password_encrypted) \
                                VALUES (?, ?, ?, ?)', (user_id, name, username, password))
            self.conn.commit()
            return InsertStatus.SUCCESS
        except sqlite3.IntegrityError as e:
            print(f'Error adding user: {e}')
            self.conn.rollback()
            return InsertStatus.OTHER_ERROR

    def get_user(self, username: str):
        pass

    def get_login(self, name: str):
        pass
