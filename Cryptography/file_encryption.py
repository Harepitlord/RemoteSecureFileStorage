"""
File encryption utilities for shipment documents
"""
import os
import hashlib
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import FileEncryptionKey
from .Encryption import SyncEncrypt, AsyncEncrypt
from UserManagement.models import UserGroups

CustomUser = get_user_model()


class ShipmentFileManager:
    """Manages encrypted file storage and multi-user access for shipments"""
    
    @staticmethod
    def encrypt_and_store_file(file, shipment, uploader):
        """
        Encrypt a file and create access keys for authorized users
        
        Args:
            file: Django UploadedFile object
            shipment: Shipment instance
            uploader: User who uploaded the file
            
        Returns:
            dict: Contains encrypted_path, file_hash, and created_keys count
        """
        try:
            # Create temporary file path
            temp_path = f"/tmp/{file.name}"
            
            # Save uploaded file temporarily
            with open(temp_path, 'wb+') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
            
            # Generate AES key and encrypt file
            sync_encrypt = SyncEncrypt()
            aes_key = sync_encrypt.generateKey()
            
            # Create encrypted file path
            encrypted_dir = os.path.join(settings.MEDIA_ROOT, 'encrypted_shipments', shipment.shipmentId)
            os.makedirs(encrypted_dir, exist_ok=True)
            
            # Encrypt the file
            encrypted_path = sync_encrypt.encrypt(temp_path, aes_key)
            
            # Move encrypted file to proper location
            final_encrypted_path = os.path.join(encrypted_dir, f"{file.name}.enc")
            os.rename(encrypted_path, final_encrypted_path)
            
            # Calculate file hash for integrity
            file_hash = ShipmentFileManager._calculate_file_hash(final_encrypted_path)
            
            # Create encryption keys for authorized users
            created_keys = ShipmentFileManager._create_access_keys(
                shipment, aes_key, file_hash, uploader
            )
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                'encrypted_path': final_encrypted_path,
                'file_hash': file_hash,
                'created_keys': created_keys
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise Exception(f"File encryption failed: {str(e)}")
    
    @staticmethod
    def _create_access_keys(shipment, aes_key, file_hash, uploader):
        """Create encrypted AES keys for all authorized users"""
        async_encrypt = AsyncEncrypt()
        created_keys = 0
        
        # Get all users who should have access
        authorized_users = ShipmentFileManager._get_authorized_users(shipment, uploader)
        
        for user_info in authorized_users:
            user = user_info['user']
            key_type = user_info['key_type']
            
            # Skip if user doesn't have RSA keys
            if not user.has_rsa_keys():
                continue
            
            try:
                # Encrypt AES key with user's RSA public key
                encrypted_aes_key = async_encrypt.encrypt_key(user, aes_key)
                
                # Create or update FileEncryptionKey record
                FileEncryptionKey.objects.update_or_create(
                    shipment=shipment,
                    user=user,
                    key_type=key_type,
                    defaults={
                        'encrypted_aes_key': encrypted_aes_key,
                        'file_hash': file_hash
                    }
                )
                created_keys += 1
                
            except Exception as e:
                print(f"Failed to create encryption key for user {user.email}: {str(e)}")
                continue
        
        return created_keys
    
    @staticmethod
    def _get_authorized_users(shipment, uploader):
        """Get list of users authorized to access shipment files"""
        authorized_users = []
        
        # 1. Shipment owner (uploader)
        authorized_users.append({
            'user': uploader,
            'key_type': 'OWNER'
        })
        
        # 2. Assigned logistics users
        for assignment in shipment.assignments.filter(is_active=True):
            authorized_users.append({
                'user': assignment.logistics_user,
                'key_type': 'ASSIGNED'
            })
        
        # 3. All authority users
        authority_users = CustomUser.objects.filter(
            role=UserGroups.authority,
            is_active=True
        )
        
        for authority_user in authority_users:
            authorized_users.append({
                'user': authority_user,
                'key_type': 'AUTHORITY'
            })
        
        return authorized_users
    
    @staticmethod
    def _calculate_file_hash(file_path):
        """Calculate SHA-256 hash of file for integrity verification"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    def decrypt_file_for_user(shipment, user, output_path=None):
        """
        Decrypt shipment file for authorized user
        
        Args:
            shipment: Shipment instance
            user: User requesting access
            output_path: Optional path for decrypted file
            
        Returns:
            str: Path to decrypted file
        """
        try:
            # Check if user has access
            encryption_key = FileEncryptionKey.objects.filter(
                shipment=shipment,
                user=user
            ).first()
            
            if not encryption_key:
                raise Exception("User does not have access to this shipment's files")
            
            # Decrypt AES key using user's RSA private key
            from .Encryption import AsyncDecrypt
            async_decrypt = AsyncDecrypt()
            aes_key = async_decrypt.decrypt_key(user, encryption_key.encrypted_aes_key)
            
            # Find encrypted file
            encrypted_dir = os.path.join(settings.MEDIA_ROOT, 'encrypted_shipments', shipment.shipmentId)
            encrypted_files = [f for f in os.listdir(encrypted_dir) if f.endswith('.enc')]
            
            if not encrypted_files:
                raise Exception("No encrypted files found for this shipment")
            
            encrypted_file_path = os.path.join(encrypted_dir, encrypted_files[0])
            
            # Decrypt file
            from .Encryption import SyncDecrypt
            sync_decrypt = SyncDecrypt()
            
            if output_path is None:
                output_path = f"/tmp/decrypted_{shipment.shipmentId}_{user.id}.tmp"
            
            decrypted_path = sync_decrypt.decrypt(encrypted_file_path, aes_key)
            
            # Verify file integrity
            current_hash = ShipmentFileManager._calculate_file_hash(encrypted_file_path)
            if current_hash != encryption_key.file_hash:
                raise Exception("File integrity check failed")
            
            return decrypted_path
            
        except Exception as e:
            raise Exception(f"File decryption failed: {str(e)}")
    
    @staticmethod
    def add_user_access(shipment, new_user, key_type='ASSIGNED'):
        """Add access for a new user to existing shipment files"""
        try:
            # Get existing file encryption key to get AES key
            existing_key = FileEncryptionKey.objects.filter(shipment=shipment).first()
            if not existing_key:
                raise Exception("No encryption keys found for this shipment")
            
            # Decrypt AES key using an authority user's key
            authority_user = CustomUser.objects.filter(
                role=UserGroups.authority,
                is_active=True
            ).first()
            
            if not authority_user:
                raise Exception("No authority user available to decrypt keys")
            
            from .Encryption import AsyncDecrypt, AsyncEncrypt
            async_decrypt = AsyncDecrypt()
            async_encrypt = AsyncEncrypt()
            
            # Get authority's encryption key
            authority_key = FileEncryptionKey.objects.filter(
                shipment=shipment,
                user=authority_user,
                key_type='AUTHORITY'
            ).first()
            
            if not authority_key:
                raise Exception("Authority encryption key not found")
            
            # Decrypt AES key
            aes_key = async_decrypt.decrypt_key(authority_user, authority_key.encrypted_aes_key)
            
            # Encrypt for new user
            encrypted_aes_key = async_encrypt.encrypt_key(new_user, aes_key)
            
            # Create new encryption key record
            FileEncryptionKey.objects.create(
                shipment=shipment,
                user=new_user,
                key_type=key_type,
                encrypted_aes_key=encrypted_aes_key,
                file_hash=authority_key.file_hash
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to add user access: {str(e)}")
