from util.setup_logger import setup_logger

from core.cli import CLIHandler
from db.database import DatabaseManager

def main():
    setup_logger()
    db = DatabaseManager()
    user_handler = CLIHandler(db)

    print('Hello, welcome to the cosmicc password manager. Currently this is a cli only password manager which can securely store you passwords and handle multiple users. \
        Please enter if you would like to create an account or sign into an existing account.')
    print('1) Create an account')
    print('2) Sign into an account')
    print('3) Exit the program')

    while True:
        choice = input('Please select a choice (1-3):')
        match choice:
            case '1':
                user_handler.register()
                break
            case '2':
                user_handler.signin()
                break
            case '3':
                print('Have a nice day')
                break
            case _:
                print('Invalid choice')

    user_handler.run()






if __name__ == '__main__':
    main()
