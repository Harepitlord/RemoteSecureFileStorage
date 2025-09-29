#!/usr/bin/env python3
"""
Test script for the enhanced encryption system
"""
import os
import sys
import tempfile
import django
from django.test import TestCase

# Setup Django environment
sys.path.append('/Users/hareeswaran/PycharmProjects/RemoteSecureFileStorage')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemoteSecureFileStorage.settings')
django.setup()

from Cryptography.Encryption import SyncEncrypt, SyncDecrypt, RSAKeyManager


class EncryptionSystemTests(TestCase):
    """Test cases for the enhanced encryption system"""

    def test_aes_gcm_encryption_decryption(self):
        """Test AES-GCM 256-bit encryption/decryption"""
        print("Testing AES-GCM 256-bit encryption...")
        
        # Create test data
        test_data = b"This is a test file for AES-GCM encryption. " * 100
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_data)
            temp_filename = temp_file.name
        
        try:
            # Initialize encryption
            encryptor = SyncEncrypt()
            decryptor = SyncDecrypt()
            
            # Generate AES key
            aes_key = encryptor.generateKey()
            self.assertEqual(len(aes_key), 32, "AES key should be 32 bytes (256 bits)")
            
            # Encrypt file
            encrypted_filename = encryptor.encrypt(temp_filename, aes_key)
            self.assertTrue(os.path.exists(encrypted_filename), "Encrypted file should exist")
            
            # Decrypt file
            decrypted_filename = decryptor.decrypt(encrypted_filename, aes_key)
            self.assertTrue(os.path.exists(decrypted_filename), "Decrypted file should exist")
            
            # Verify decryption
            with open(decrypted_filename, 'rb') as f:
                decrypted_data = f.read()
            
            self.assertEqual(decrypted_data, test_data, "Decrypted data should match original")
            print("✅ AES-GCM encryption/decryption test PASSED")
                
        finally:
            # Cleanup
            for filename in [temp_filename, encrypted_filename, decrypted_filename]:
                if os.path.exists(filename):
                    os.unlink(filename)

    def test_rsa_key_generation(self):
        """Test RSA key pair generation"""
        print("Testing RSA key pair generation...")
        
        private_pem, public_pem = RSAKeyManager.generate_key_pair(2048)
        
        # Verify key lengths
        self.assertGreater(len(private_pem), 1000, "Private key should be substantial length")
        self.assertGreater(len(public_pem), 400, "Public key should be substantial length")
        
        # Verify keys start with correct headers
        self.assertTrue(private_pem.startswith('-----BEGIN PRIVATE KEY-----'), 
                       "Private key should have correct PEM header")
        self.assertTrue(public_pem.startswith('-----BEGIN PUBLIC KEY-----'), 
                       "Public key should have correct PEM header")
        
        print("✅ RSA key generation test PASSED")


def run_standalone_tests():
    """Run tests outside of Django test framework"""
    print("Enhanced Encryption System Test")
    print("=" * 40)
    
    # Create test instance
    test_instance = EncryptionSystemTests()
    
    try:
        test_instance.test_aes_gcm_encryption_decryption()
        test_instance.test_rsa_key_generation()
        print("\nAll encryption tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_standalone_tests()
