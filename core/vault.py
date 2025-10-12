from core.encryption import EncryptionManager
from db.database import DatabaseManager


class Vault:
    def __init__(self, db: DatabaseManager) -> None:
        self.database: DatabaseManager = db

    # Creates new user
    def create_user(self, username: str, password: str):
        pass

    # Check if the password is the master password of the user given their id
    def check_master_password(self, user_id: int, password: str) -> bool:
        pass

    # Adds the username and password as a new login to the manager under the name
    def add_login(self, user_id: int, name: str, username: str, password: str):
        pass

    # Removes the login with the following name
    def remove_login(self, user_id: int, name: str):
        pass

    # Retreives the password with the following name
    def get_login_information(self, user_id: int, name: str):
        pass

    # Lists all passwords
    def list_logins(self, user_id: int):
        pass

    def remove_user(self, user_id: int):
        pass
