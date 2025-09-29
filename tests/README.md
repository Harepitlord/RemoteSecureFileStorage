# RemoteSecureFileStorage Tests

This package contains comprehensive tests for the RemoteSecureFileStorage project's enhanced encryption and security features.

## Test Structure

```
tests/
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── run_all_tests.py           # Standalone test runner
├── test_encryption.py         # Encryption system tests
└── test_vault_system.py       # Vault system tests
```

## Test Categories

### 1. Encryption System Tests (`test_encryption.py`)
- **AES-GCM 256-bit Encryption/Decryption**: Tests the enhanced symmetric encryption
- **RSA Key Generation**: Tests RSA key pair generation with proper PEM formatting

### 2. Vault System Tests (`test_vault_system.py`)
- **Custom Encryption Manager**: Tests the Django-integrated encryption utilities
- **User Key Generation & Vault Storage**: Tests secure private key storage
- **Full Encryption Workflow**: Tests complete end-to-end encryption process

## Running Tests

### Option 1: Django Test Framework (Recommended)
```bash
# Run all tests
python manage.py test tests --verbosity=2

# Run specific test file
python manage.py test tests.test_encryption --verbosity=2
python manage.py test tests.test_vault_system --verbosity=2

# Run specific test method
python manage.py test tests.test_encryption.EncryptionSystemTests.test_aes_gcm_encryption_decryption
```

### Option 2: Standalone Test Runner
```bash
# Run all tests
python tests/run_all_tests.py

# Run individual test files
python tests/test_encryption.py
python tests/test_vault_system.py
```

### Option 3: Pytest (if installed)
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_encryption.py -v
```

## Test Features

- **Comprehensive Coverage**: Tests all major encryption and vault functionality
- **Automatic Cleanup**: All tests clean up temporary files and database records
- **Detailed Output**: Clear success/failure messages with descriptive information
- **Django Integration**: Uses Django's test database and ORM features
- **Standalone Capability**: Can run outside Django test framework

## Test Data

Tests use:
- Temporary files for encryption/decryption testing
- In-memory test database for Django model testing
- Randomly generated test users (automatically cleaned up)
- Sample data that exercises all code paths

## Security Considerations

- Tests use the same encryption algorithms as production
- Private keys are properly stored in the encrypted vault during testing
- No sensitive data is logged or persisted after tests complete
- Test database is isolated and destroyed after each test run
