import os
import secrets

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class SyncEncrypt:
    """Enhanced AES-GCM 256-bit encryption for secure file storage"""
    AES_KEY_SIZE = 32  # 256 bits
    AES_NONCE_SIZE = 12  # 96 bits for GCM
    AES_TAG_SIZE = 16  # 128 bits

    def generateKey(self):
        """Generate a secure 256-bit AES key"""
        return secrets.token_bytes(self.AES_KEY_SIZE)

    def encrypt(self, filename, key):
        """
        Encrypt file using AES-GCM 256-bit
        Returns: output filename
        """
        chunk_size = 64 * 1024
        output_filename = filename + ".encrypted"
        filesize = str(os.path.getsize(filename)).zfill(16)
        nonce = secrets.token_bytes(self.AES_NONCE_SIZE)

        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        with open(filename, 'rb') as infile:
            with open(output_filename, 'wb') as outfile:
                # Write metadata
                outfile.write(filesize.encode('utf-8'))
                outfile.write(nonce)

                # Reserve space for tag (will be written at the end)
                tag_position = outfile.tell()
                outfile.write(b'\x00' * self.AES_TAG_SIZE)

                # Encrypt file in chunks
                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break

                    ciphertext = encryptor.update(chunk)
                    outfile.write(ciphertext)

                # Finalize encryption and get tag
                encryptor.finalize()
                tag = encryptor.tag

                # Write tag at reserved position
                current_position = outfile.tell()
                outfile.seek(tag_position)
                outfile.write(tag)
                outfile.seek(current_position)

        return output_filename


class AsyncEncrypt:
    """Enhanced RSA encryption for AES key protection"""

    def encrypt_key(self, user, aes_key):
        """
        Encrypt AES key using RSA-OAEP with SHA-256
        Args:
            user: User object with public key
            aes_key: AES key bytes to encrypt
        Returns: encrypted AES key bytes
        """
        # Load public key from user
        public_key = serialization.load_pem_public_key(
            user.public_key_pem.encode('utf-8'),
            backend=default_backend()
        )

        # Encrypt using RSA-OAEP with SHA-256
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted_aes_key


class SyncDecrypt:
    """Enhanced AES-GCM 256-bit decryption"""
    AES_NONCE_SIZE = 12  # 96 bits for GCM
    AES_TAG_SIZE = 16  # 128 bits

    def decrypt(self, filename, key, output_filename=None):
        """
        Decrypt file using AES-GCM 256-bit
        Args:
            filename: encrypted file path
            key: AES decryption key
            output_filename: optional output filename
        Returns: decrypted filename
        """
        if output_filename is None:
            output_filename = filename.replace('.encrypted', '_decrypted')

        with open(filename, 'rb') as infile:
            # Read metadata
            filesize_str = infile.read(16).decode('utf-8')
            original_size = int(filesize_str)
            nonce = infile.read(self.AES_NONCE_SIZE)
            tag = infile.read(self.AES_TAG_SIZE)

            # Create AES-GCM cipher for decryption
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            with open(output_filename, 'wb') as outfile:
                # Decrypt file in chunks
                chunk_size = 64 * 1024
                bytes_written = 0

                while bytes_written < original_size:
                    # Read chunk, but don't exceed original file size
                    remaining = original_size - bytes_written
                    chunk_to_read = min(chunk_size, remaining)

                    chunk = infile.read(chunk_to_read)
                    if len(chunk) == 0:
                        break

                    plaintext = decryptor.update(chunk)
                    outfile.write(plaintext)
                    bytes_written += len(plaintext)

                # Finalize decryption (verifies tag)
                decryptor.finalize()

        return output_filename


class AsyncDecrypt:
    """Enhanced RSA decryption for AES key recovery"""

    def decrypt_key(self, user, encrypted_key):
        """
        Decrypt AES key using RSA-OAEP with SHA-256
        Args:
            user: User object with private key
            encrypted_key: encrypted AES key bytes
        Returns: decrypted AES key bytes
        """
        # Get private key from secure vault
        private_key_pem = user.get_private_key()
        if not private_key_pem:
            raise ValueError("No private key found for user")

        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        # Decrypt using RSA-OAEP with SHA-256
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return aes_key


class RSAKeyManager:
    """RSA key pair generation and management"""

    @staticmethod
    def generate_key_pair(key_size=2048):
        """
        Generate RSA key pair
        Args:
            key_size: RSA key size in bits (default: 2048)
        Returns: tuple (private_key_pem, public_key_pem)
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

        # Get public key
        public_key = private_key.public_key()

        # Serialize private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # Serialize public key to PEM format
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return private_pem, public_pem
