from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    master_hash: str
    salt: str

@dataclass
class VaultEntry:
    id: int
    user_id: int
    service_name: str
    username: str
    password_encrypted: str
