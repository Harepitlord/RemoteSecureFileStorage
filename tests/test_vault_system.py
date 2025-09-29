#!/usr/bin/env python3
"""
Test script for the custom vault encryption system
"""
import os
import sys
import django
from django.test import TestCase

# Setup Django environment
sys.path.append('/Users/hareeswaran/PycharmProjects/RemoteSecureFileStorage')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemoteSecureFileStorage.settings')
django.setup()

from UserManagement.models import CustomUser, UserPrivateKeyVault, EncryptionManager
from Cryptography.Encryption import RSAKeyManager, AsyncEncrypt, AsyncDecrypt, SyncEncrypt


class VaultSystemTests(TestCase):
    """Test cases for the custom vault encryption system"""

    def test_encryption_manager(self):
        """Test the custom encryption manager"""
        print("Testing EncryptionManager...")
        
        # Test data
        test_data = "This is a secret private key for testing!"
        
        # Encrypt
        encrypted = EncryptionManager.encrypt_data(test_data)
        self.assertIsNotNone(encrypted, "Encrypted data should not be None")
        self.assertNotEqual(encrypted, test_data, "Encrypted data should be different from original")
        
        # Decrypt
        decrypted = EncryptionManager.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data, "Decrypted data should match original")
        
        print("✅ EncryptionManager test PASSED")

    def test_user_key_generation_and_vault_storage(self):
        """Test user RSA key generation and vault storage"""
        print("Testing User RSA Key Generation and Vault Storage...")
        
        # Create test user
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            country='US',
            phone_no='1234567890'
        )
        
        try:
            # Initially user should not have keys
            self.assertFalse(user.has_rsa_keys(), "User should not have keys initially")
            
            # Generate RSA keys
            private_pem, public_pem = user.generate_rsa_keys()
            user.save()
            
            # Verify key generation
            self.assertTrue(user.has_rsa_keys(), "User should have keys after generation")
            self.assertIsNotNone(user.private_key_vault_id, "Vault ID should be set")
            self.assertGreater(len(public_pem), 400, "Public key should be substantial length")
            self.assertGreater(len(private_pem), 1000, "Private key should be substantial length")
            
            # Test key retrieval
            retrieved_public = user.get_public_key()
            retrieved_private = user.get_private_key()
            
            self.assertEqual(retrieved_public, public_pem, "Retrieved public key should match")
            self.assertEqual(retrieved_private, private_pem, "Retrieved private key should match")
            
            # Test vault model directly
            vault = UserPrivateKeyVault.objects.get(vault_id=user.private_key_vault_id)
            self.assertEqual(vault.user, user, "Vault should be linked to correct user")
            self.assertIsNotNone(vault.created_at, "Vault should have creation timestamp")
            
            print("✅ User key generation and vault storage test PASSED")
            
        finally:
            # Cleanup
            user.delete()

    def test_full_encryption_workflow(self):
        """Test complete encryption workflow with vault"""
        print("Testing Full Encryption Workflow...")
        
        # Create test user
        user = CustomUser.objects.create_user(
            email='workflow@example.com',
            password='testpass123',
            name='Workflow User',
            country='US',
            phone_no='1234567890'
        )
        
        try:
            # Generate keys
            user.generate_rsa_keys()
            user.save()
            
            # Test AES key encryption/decryption
            sync_encrypt = SyncEncrypt()
            aes_key = sync_encrypt.generateKey()
            
            # Encrypt AES key with user's RSA public key
            async_encrypt = AsyncEncrypt()
            encrypted_aes_key = async_encrypt.encrypt_key(user, aes_key)
            
            self.assertEqual(len(aes_key), 32, "AES key should be 32 bytes")
            self.assertGreater(len(encrypted_aes_key), 200, "Encrypted AES key should be substantial")
            
            # Decrypt AES key with user's RSA private key
            async_decrypt = AsyncDecrypt()
            decrypted_aes_key = async_decrypt.decrypt_key(user, encrypted_aes_key)
            
            self.assertEqual(decrypted_aes_key, aes_key, "Decrypted AES key should match original")
            
            print("✅ Full encryption workflow test PASSED")
            
        finally:
            # Cleanup
            user.delete()


def run_standalone_tests():
    """Run tests outside of Django test framework"""
    print("Custom Vault Encryption System Test")
    print("=" * 50)
    
    # Create test instance
    test_instance = VaultSystemTests()
    
    try:
        test_instance.test_encryption_manager()
        test_instance.test_user_key_generation_and_vault_storage()
        test_instance.test_full_encryption_workflow()
        print("\nAll vault system tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_standalone_tests()
