# Cosmicc Password Manager

A secure, locally-stored password manager built with Python. Store and manage your passwords safely with strong encryption and multi-user support.

## Features

- **Strong Encryption**: Uses Fernet (AES-256) encryption with Scrypt key derivation
- **Multi-User Support**: Multiple users can maintain separate vaults on the same system
- **Local Storage**: All data stored locally in SQLite database - no cloud dependencies
- **Secure Master Password**: Master password requirements enforce strong security practices
- **Service Management**: Store multiple accounts per service (e.g., personal and work Gmail)
- **Safety Features**: Confirmation prompts for destructive actions, attempt limits on login

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cosmicc-password-manager.git
cd cosmicc-password-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### First Time Setup

1. Run the application
2. Select "Create an account"
3. Choose an alphanumeric username
4. Create a master password meeting these requirements:
   - At least 15 characters long
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character (!@#$%^&*(),.?:|<>_-)

### Managing Passwords

Once signed in, you can:

- **Add a new login**: Store credentials for a service
- **List all logins**: View all stored credentials
- **Search by service name**: Find specific login(s)
- **Delete a login**: Remove stored credentials
- **User settings**: Change username or delete account
- **Sign out**: Switch users or exit safely

### Security Features

- **Encrypted Storage**: All passwords encrypted with your master password as the key
- **Secure Key Derivation**: Uses Scrypt (N=2^14, r=8, p=1) for key generation
- **Login Attempt Limits**: Maximum 5 attempts before lockout
- **Per-User Encryption**: Each user's vault is encrypted with their unique master password
- **No Password Recovery**: Forgotten master passwords cannot be recovered (by design)

## Testing

Run the test suite with pytest:

```bash
pytest tests/
```

Tests cover:
- Database operations
- Encryption/decryption
- User management
- Vault operations

## Roadmap

### Short Term
- [ ] Expand unit test coverage
- [ ] Add password generator functionality
- [ ] Implement password strength checker for stored passwords
- [ ] GUI interface (likely using tkinter or PyQt)
- [ ] Two-factor authentication support for master password

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
