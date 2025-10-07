import logging
import os

from pythonjsonlogger import jsonlogger


def setup_logger():
    # Makes the log file and directory
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    # Creates the logger and handler and formatter
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')

    # Sets the handler and formatter
    handler.setFormatter(formatter)
    logger.addHandler(handler)
