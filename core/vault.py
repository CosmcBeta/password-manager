from core.data_models import User, VaultEntry
from core.encryption import EncryptionManager
from db.database import DatabaseManager
from util.enums import InsertStatus, RemoveStatus


class Vault:
    def __init__(self, db: DatabaseManager) -> None:
        self.database: DatabaseManager = db
        self.encryption: EncryptionManager = EncryptionManager()

    # Creates new user
    def create_user(self, username: str, password: str) -> InsertStatus:
        salt, hash = self.encryption.hash_master_password(password)
        return self.database.insert_user(username, hash, salt)

    # Check if the password is the master password of the user given their id
    def check_master_password(self, user: User, password: str) -> bool:
        return self.encryption.vertify_master_password(password, user.salt, user.master_hash)

    # Adds the username and password as a new login to the manager under the name
    def add_login(self, user: User, service_name: str, username: str | None, password: str) -> InsertStatus:
        encrypted_password = self.encryption.encrypt_password(user.master_hash, password)
        return self.database.insert_login(user.id, service_name, username, encrypted_password)

    # Lists all passwords
    def list_logins(self, user: User) -> None:
        logins = self.database.get_user_logins(user.id)
        if not logins:
            print('You have no logins.')
            return

        for login in logins:
            decrypted_password = self.encryption.decrypt_password(user.master_hash, login.password_encrypted)
            username_display = login.username if login.username else 'N/A'
            print(f'Service: {login.service_name} | Username: {username_display} | Password: {decrypted_password.decode()}')

    # Deletes user from database
    def remove_user(self, user: User) -> RemoveStatus:
        return self.database.delete_user(user.id)

    # Helper to select from multiple logins
    def _select_login_from_list(self, logins: list[VaultEntry], action: str) -> VaultEntry | None:
        print(f'\nFound {len(logins)} logins:')
        for i, login in enumerate(logins, 1):
            print(f'{i}. Username: {login.username if login.username else "N/A"}')

        while True:
            choice = input(f'\nSelect which login to {action} (1-{len(logins)}) or \'cancel\': ').strip()
            if choice == 'cancel':
                print('Cancelled.')
                return None
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(logins):
                    return logins[idx]
                else:
                    print(f'Invalid choice. Please enter a number between 1 and {len(logins)}.')
            except ValueError:
                print('Invalid input. Please enter a number.')

    # Removes a login based on the name
    def remove_login(self, user: User, service_name: str) -> RemoveStatus:
        logins = self.database.get_logins_from_name(user.id, service_name)

        if not logins or logins == []:
            print(f'No logins found for \'{service_name}\'')
            return RemoveStatus.ERROR

        if len(logins) == 1:
            login = logins[0]
        else:
            login = self._select_login_from_list(logins, 'delete')
            if login is None:
                return RemoveStatus.ERROR

        confirm = input(f'Delete login for \'{service_name}\' (username: {login.username})? (yes/no): ').strip().lower()
        if confirm == 'yes':
            return self.database.delete_login(login.id)
        else:
            print('Deletion cancelled.')
            return RemoveStatus.ERROR

    # Gets the information for a login given the user and service name
    def get_login_information(self, user: User, service_name: str) -> None:
        logins = self.database.get_logins_from_name(user.id, service_name)

        if not logins:
            print(f'No logins found for \'{service_name}\'')
            return

        if len(logins) == 1:
            login = logins[0]
        else:
            login = self._select_login_from_list(logins, 'view')
            if login is None:
                return

        decrypted_password = self.encryption.decrypt_password(user.master_hash, login.password_encrypted)
        print('\n--- Login Information ---')
        print(f'Service: {login.service_name}')
        print(f'Username: {login.username if login.username else "N/A"}')
        print(f'Password: {decrypted_password.decode()}')
        print()
