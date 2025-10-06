🧠 File roles
main.py

Handles CLI flow:

Ask for username

Check if user exists (calls UserHandler)

If yes → ask for master password and verify

If no → create new user and store hash

Once logged in, call vault operations (view/add/delete credentials)

user_handler.py

Manages users:

create_user(username, master_password)

authenticate_user(username, master_password)

get_user_id(username)

Uses the database module to check if the user exists and uses the encryption module to hash passwords.

vault.py

Handles vault operations:

add_entry(user_id, service, username, password)

get_entries(user_id)

delete_entry(user_id, entry_id)

Uses encryption for stored passwords.

encryption.py

Handles all cryptographic functions:

Generate salts

Hash and verify master passwords

Encrypt/decrypt service passwords (using user’s master password or a derived key)

database.py

Handles all SQLite logic:

Connecting to database

Creating tables (users and vault_entries)

Querying and committing data
