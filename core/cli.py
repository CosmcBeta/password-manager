import re
import sys

from core.data_models import User
from core.vault import Vault
from db.database import DatabaseManager
from util.enums import InsertStatus, RemoveStatus


class CLIHandler:
    def __init__(self, db: DatabaseManager) -> None:
        self.database: DatabaseManager = db
        self.vault: Vault = Vault(db)
        self.user: User | None = None

    # Handles registering with user
    def register(self) -> bool:
        username = self.create_username()

        if username is None:
            return False

        print('Create a password with the following requirements (type \'exit\' to quit):')
        print('- At least 15 characters long')
        print('- At least one uppercase letter')
        print('- At least one lowercase letter')
        print('- At least one number')
        print('- At least one special character (!@#$%^&*(),.?:|<>_-)')
        print()

        while True:
            password = input('Enter your password: ')
            if password == 'exit':
                print('Exiting registration')
                return False
            elif self.check_password_vaild(password):
                print('Password accepted.')
                break

        result = self.vault.create_user(username, password)
        return result == InsertStatus.SUCCESS

    # Checks if the password meets the requirements
    def check_password_vaild(self, password: str) -> bool:
        if len(password) < 15:
            print('Password must be at least 15 characters long. Please try again.')
            return False

        if not re.search(r'[A-Z]', password):
            print('Password must contain at least one uppercase letter. Please try again.')
            return False

        if not re.search(r'[a-z]', password):
            print('Password must contain at least one lowercase letter. Please try again.')
            return False

        if not re.search(r'\d', password):
            print('Password must contain at least one number. Please try again.')
            return False

        if not re.search(r'[!@#$%^&*(),.?:|<>_-]', password):
            print('Password must contain at least one special character (!@#$%^&*(),.?:|<>_-). Please try again.')
            return False

        if not re.match(r'^[A-Za-z0-9!@#$%^&*(),.?:|<>_-]+$', password):
            print('Password contains invalid characters. Please try again.')
            return False

        return True

    # Handles signing the user into the vault
    def signin(self) -> bool:
        while True:
            username = input('Please enter your username (or \'exit\' to quit): ')
            if username == 'exit':
                print('Exiting sign in.')
                return False

            user = self.database.get_user_from_username(username)
            if user is not None:
                print('User found!')
                break
            else:
                print('User not found. Please try again.')

        max_attempts = 5
        for attempt in range(max_attempts):
            password = input('Please enter your master password (\'exit\' to quit): ')
            if password == 'exit':
                print('Exiting sign in.')
                return False

            if self.vault.check_master_password(user, password):
                print('Password accepted!')
                self.user = user
                return True
            else:
                attempts_left = max_attempts - attempt - 1
                if attempts_left > 0:
                    print(f'Incorrect password. You have {attempts_left} attempt(s) remaining.')
                else:
                    print('Maximum attempts reached. Exiting for security.')
                    return False

        return False

    # Validates and returns non-empty input
    def get_non_empty_input(self, prompt: str, allow_skip: bool = False) -> str | None:
        while True:
            value = input(prompt).strip()
            if value == 'exit':
                print('Cancelled.')
                return None
            if not value:
                if allow_skip:
                    return None
                print('This field cannot be empty. Please try again or type \'exit\' to cancel.')
                continue
            return value

    # Runs the program and controls the input and output
    def run(self) -> None:
        if self.user is None:
            print('Error: No user signed in.')
            return

        while True:
            user_choice = self.display_menu()

            match user_choice:
                case '1':
                    print('\n--- Adding new login ---')
                    name = self.get_non_empty_input('Service name: ')
                    if name is None:
                        continue

                    username = self.get_non_empty_input('Username: ', allow_skip=True)
                    password = self.get_non_empty_input('Password: ')
                    if password is None:
                        continue

                    status = self.vault.add_login(self.user, name, username, password)
                    if status == InsertStatus.SUCCESS:
                        print('Login added successfully!')
                    else:
                        print('Failed to add login.')

                case '2':
                    print('\n--- All Logins ---')
                    self.vault.list_logins(self.user)

                case '3':
                    print('\n--- Search Logins ---')
                    name = self.get_non_empty_input('Service name to search: ')
                    if name is not None:
                        self.vault.get_login_information(self.user, name)

                case '4':
                    print('\n--- Delete Login ---')
                    name = self.get_non_empty_input('Service name to delete: ')
                    if name is not None:
                        confirm = input(f'Are you sure you want to delete \'{name}\'? (yes/no): ').strip().lower()
                        if confirm == 'yes':
                            status = self.vault.remove_login(self.user, name)
                            if status == RemoveStatus.SUCCESS:
                                print('Login deleted successfully!')
                            else:
                                print('Failed to delete login.')
                        else:
                            print('Deletion cancelled.')

                case '5':
                    print('\n--- User Settings ---')
                    self.list_user_settings()

                case '6':
                    print('\n--- Sign Out ---')
                    self.user = None
                    print('Signed out successfully.')
                    return

                case '7':
                    print('Exiting password manager. Goodbye!')
                    return

                case _:
                    pass

    # Displays menu
    def display_menu(self) -> str:
        if self.user is None:
            return ""

        print()
        print(f'Welcome {self.user.username}! What would you like to do?')
        print()
        print('1. Enter a new login')
        print('2. List all logins')
        print('3. List logins by name')
        print('4. Delete a login')
        print('5. User settings')
        print('6. Sign out')
        print('7. Exit')
        print()

        while True:
            choice = input('\nSelect an option (1-7): ').strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print('Invalid choice. Please enter a number between 1 and 7.')

    # Goes through the options for use settings
    def list_user_settings(self) -> None:
        if self.user is None:
            return

        print('\n--- User Settings ---')
        print(f'Current username: {self.user.username}')
        print('1. Delete account')
        print('2. Change username')
        print('3. Back to main menu')

        while True:
            choice = input('\nSelect an option (1-3): ').strip()
            if choice in ['1', '2', '3']:
                break
            else:
                print('Invalid choice. Please enter a number between 1 and 3.')

        match choice:
            case '1':
                print('\n--- Delete Account ---')
                confirm = input(f'Are you sure you want to delete your account \'{self.user.username}\'? This cannot be undone. (yes/no): ').strip().lower()
                if confirm == 'yes':
                    status = self.vault.remove_user(self.user)
                    if status == RemoveStatus.SUCCESS:
                        print('Account deleted successfully. Goodbye!')
                        self.user = None
                        sys.exit(0)
                    else:
                        print('Failed to delete account.')
                else:
                    print('Account deletion cancelled.')
            case '2':
                print('\n--- Change Username ---')
                username = self.create_username()
                if username is not None:
                    status = self.database.update_username(self.user.id, username)
                    if status == InsertStatus.SUCCESS:
                        self.user.username = username
                        print(f'Username changed successfully to \'{username}\'!')
                    else:
                        print('Failed to change username. It may already be taken.')
            case '3':
                return
            case _:
                pass

    # Changes the username for the current user
    def create_username(self) -> str | None:
        print('Username must be alphanumeric (only letters and numbers).')
        while True:
            username = input('Please enter your username (or \'exit\' to cancel): ').strip()
            if username == 'exit':
                print('Cancelled.')
                return None
            elif not username:
                print('Username cannot be empty. Please try again.')
            elif username.isalnum():
                print('Username accepted.')
                return username
            else:
                print('Username must only contain letters and numbers. Please try again.')
