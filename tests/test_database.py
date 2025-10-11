from db.database import DatabaseManager
from core.enums import InsertStatus

import pytest

@pytest.fixture
def db():
    db = DatabaseManager(':memory:')
    yield db
    db.conn.close()

def test_insert_user_success(db: DatabaseManager):
    status = db.insert_user("alice", "hash123", "salt123")
    assert status == InsertStatus.SUCCESS

    user = db.get_user_from_username("alice")
    assert user is not None
    assert user.username == "alice"
    assert user.master_hash == "hash123"
    assert user.salt == "salt123"

def test_insert_user_duplicate(db: DatabaseManager):
    user_status = db.insert_user("bob", "hashA", "saltA")
    assert user_status == InsertStatus.SUCCESS

    status = db.insert_user("bob", "hashB", "saltB")
    assert status == InsertStatus.ERROR
    # assert status == InsertStatus.DUBLICATE_USERNAME

def test_insert_login_success(db: DatabaseManager):
    user_status = db.insert_user("charlie", "hashC", "saltC")
    assert user_status == InsertStatus.SUCCESS

    user = db.get_user_from_username("charlie")
    assert user is not None
    status = db.insert_login(user.id, "GitHub", "charlie123", "passC")
    assert status == InsertStatus.SUCCESS

    logins = db.get_user_logins(user.id)
    assert len(logins) == 1
    assert logins[0] is not None
    assert logins[0].service_name == "GitHub"

def test_get_logins_from_name(db: DatabaseManager):
    status_dana = db.insert_user("dana", "hashD", "saltD")
    assert status_dana == InsertStatus.SUCCESS

    user = db.get_user_from_username("dana")
    assert user is not None

    status_twitter = db.insert_login(user.id, "Twitter", "dana_t", "pwD1")
    assert status_twitter == InsertStatus.SUCCESS
    status_twitter_alt = db.insert_login(user.id, "Twitter", "dana_alt", "pwD2")
    assert status_twitter_alt == InsertStatus.SUCCESS

    logins = db.get_logins_from_name(user.id, "Twitter")
    assert len(logins) == 2
    usernames = {l.username for l in logins if l is not None}
    assert {"dana_t", "dana_alt"} <= usernames

def test_get_user_logins_empty(db: DatabaseManager):
    user_status = db.insert_user("empty", "hashE", "saltE")
    assert user_status == InsertStatus.SUCCESS

    user = db.get_user_from_username("empty")
    assert user is not None

    logins = db.get_user_logins(user.id)
    assert logins == [None]
