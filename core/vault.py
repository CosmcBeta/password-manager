from core.encryption import EncryptionManager
from db.database import DatabaseManager


class Vault:
    def __init__(self) -> None:
        pass

    # Adds the username and password as a new login to the manager under the name
    def add_password(self, name, username, password):
        pass

    # Removes the login with the following name
    def remove_password(self, name):
        pass

    # Retreives the password with the following name
    def get_password(self, name):
        pass

    # Lists all passwords
    def list_passwords(self):
        pass
