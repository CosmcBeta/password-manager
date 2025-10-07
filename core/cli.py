from sqlite3.dbapi2 import DatabaseError

from db.database import DatabaseManager


class CLIHandler:
    def __init__(self, db: DatabaseManager) -> None:
        self.database: DatabaseManager = db

    def register(self):
        pass

    def signin(self):
        pass

    # Runs the program and controls the input and output
    def run(self):
        pass
