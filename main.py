from core.cli import CLIHandler
from db.database import DatabaseManager
from util.setup_logger import setup_logger


def display_welcome_menu() -> str:
    print('Welcome to the cosmicc password manager! This CLI password manager securely stores your')
    print('passwords and handles multiple users.')
    print()
    print('1. Create an account')
    print('2. Sign into an account')
    print('3. Exit the program')
    print()

    while True:
        choice = input('\nPlease select a choice (1-3): ').strip()
        if choice in ['1', '2', '3']:
            return choice
        else:
            print('Invalid choice. Please enter a number between 1 and 3.')


def main():
    setup_logger()
    db = DatabaseManager()
    user_handler = CLIHandler(db)

    try:
        while True:
            choice = display_welcome_menu()

            match choice:
                case '1':
                    success = user_handler.register()
                    if success:
                        # Automatically sign in after successful registration
                        print('\nAccount created! Please sign in with your new credentials.')
                        if user_handler.signin():
                            user_handler.run()
                    else:
                        print('\nError creating account.')
                case '2':
                    if user_handler.signin():
                        user_handler.run()
                case '3':
                    print('Have a nice day!')
                    break
                case _:
                    pass

    finally:
        db.close()


if __name__ == '__main__':
    main()
