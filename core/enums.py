from enum import Enum


class InsertStatus(Enum):
    SUCCESS = 0
    DUBLICATE_USERNAME = 1
    FOREIGN_KEY_FAIL = 2
    OTHER_ERROR = 3
