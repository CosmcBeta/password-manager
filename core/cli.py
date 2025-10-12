import re
import sys

from core.data_models import User
from core.vault import Vault
from db.database import DatabaseManager
from util.enums import InsertStatus


class CLIHandler:
    def __init__(self, db: DatabaseManager) -> None:
        self.database: DatabaseManager = db
        self.vault: Vault = Vault(db)
        self.user: User# Current user

    # Handles registering with user
    def register(self):
        username = self.create_username()

        if username is None:
            return

        print('Create a password with the following requirements (type \'exit\' to quit):')
        print('- At least 15 characters long')
        print('- At least one uppercase letter')
        print('- At least one lowercase letter')
        print('- At least one number')
        print('- At least one special character')
        print()
        while True:
            password = input('Enter your password: ')
            if password == 'exit':
                print('Exiting')
                return
            elif self.check_password_vaild(password):
                print('Password accepted.')
                break

        self.vault.create_user(username, password)

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

        if not re.search(r'[^A-Za-z0-9]', password):
            print('Password must contain at least one special character. Please try again.')
            return False

        if not re.match(r'^[A-Za-z0-9!@#$%^&*(),.?:|<>_-]+$', password):
            print('Password contains invalid characters. Please try again.')
            return False

        return True

    # Handles signing the user into the vault
    def signin(self):
        while True:
            username = input('Please enter your username (or \'exit\' to quit): ')
            user = self.database.get_user_from_username(username)
            if user is not None:
                print('User found!')
                break
            else:
                print('User not found. Please try again.')

        attempt_amount = 0
        while True:
            password = input('Please enter your master password (\'exit\' to quit): ')
            attempt_amount += 1
            if self.vault.check_master_password(user.id, password):
                print('Password accepted!')
                break
            else:
                if attempt_amount < 5:
                    print(f'Password does not match the given password. You have {attempt_amount} attempts left before you can\'t try again.')
                else:
                    print('You have reached the max amount of attempts and no longer can try again.')
                    sys.exit(1)

        self.user = user


    # Runs the program and controls the input and output
    def run(self):
        user_choice = self.display_menu()

        match user_choice:
            case '1':
                print('Adding new login...')
                name = input('What would you like to name this login? (press enter to skip) ') # make sure this is valid or None
                username = input('What is the username for this login? ') # make sure this is valid
                password = input('What would you like the password to be? ') # make sure this is valid
                self.vault.add_login(self.user.id, name, username, password)
            case '2':
                print('Listing all logins...')
                self.vault.list_logins(self.user.id)
            case '3':
                print('List logins by name...')
                name = input('What is the name this login? ') # make sure this is valid or None
                self.vault.get_login_information(self.user.id, name)
            case '4':
                print('Deleting login...')
                name = input('What is the name this login? ') # make sure this is valid or None
                self.vault.remove_login(self.user.id, name)
            case '5':
                print('User settings...')
                self.list_user_settings()
            case '6':
                print('Signing out...')
                self.signin()
            case '7':
                print('Exiting password manager. Goodbye!')
                return
            case _:
                pass

    def display_menu(self) -> str:
        print(f'Welcome {self.user.username}! What would you like to do?')
        print('1. Enter a new login')
        print('2. List all logins')
        print('3. List logins by name')
        print('4. Delete a login')
        print('5. User settings')
        print('6. Change user/sign out')
        print('7. Exit')

        while True:
            choice = input('\nSelect an option (1-7): ').strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print('Invalid choice. Please enter a number between 1 and 7.')

    def list_user_settings(self):
        print(f'User settings for {self.user.username}:')
        print('1. Delete account')
        print('2. Change username')
        print('3. Exit')

        while True:
            choice = input('\nSelect an option (1-3): ').strip()
            if choice in ['1', '2', '3']:
                break
            else:
                print('Invalid choice. Please enter a number between 1 and 3.')

        match choice:
            case '1':
                print('Deleting account...')
                self.vault.remove_user(self.user.id)
            case '2':
                print('Changing username...')
                username = self.create_username()
                if username is not None:
                    status = self.database.update_username(self.user.id, username)
                    assert status == InsertStatus.SUCCESS
                    self.user.username = username
            case '3':
                print('Exiting...')
                return
            case _:
                pass

    def create_username(self) -> str | None:
        print('The username you would like to choose must be alphanumeric (only letters and numbers).')
        while True:
            username = input('Please enter your username: ')
            if username == 'exit':
                print('Exiting')
                return None
            elif username.isalnum():
                print('Username accepted.')
                return username
            else:
                print('Username not accepted. please try again or type \'exit\' to quit.')
