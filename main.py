from core.cli import CLIHandler
from db.database import DatabaseManager
from util.setup_logger import setup_logger


def main():
    setup_logger()
    db = DatabaseManager()
    user_handler = CLIHandler(db)

    print('Welcome to the cosmicc password manager! This CLI password manager securely stores your')
    print('passwords and handles multiple users.')
    print('1. Create an account')
    print('2. Sign into an account')
    print('3. Exit the program')

    while True:
        choice = input('\nPlease select a choice (1-3): ').strip()
        match choice:
            case '1':
                user_handler.register()
                break
            case '2':
                user_handler.signin()
                break
            case '3':
                print('Have a nice day!')
                return
            case _:
                print('Invalid choice. Please enter a number between 1 and 3.')

    user_handler.run()

    db.close()



if __name__ == '__main__':
    main()
