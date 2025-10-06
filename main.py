import logging

def main():

    username = input('Hello, welcome to the cosmicc password manager! This is a simple password manager that takes place in the cli. \
        If you already have an account please enter your username. If you don\'t already have an account enter a username \
        to get started with the account creation process: ')

def configure_logging() -> None:
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(levelname)s - %(message)s",

    )






if __name__ == '__main__':
    main()
