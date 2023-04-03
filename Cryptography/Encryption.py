import os

from random import Random

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import padding,utils
from cryptography.hazmat.primitives.ciphers import algorithms


class SyncEncrypt:
    AES_BlockSize = 128

    def generateKey(self):
        return os.urandom(self.AES_BlockSize)

    def encrypt(self,filename,key):
        chunk_size = 64 * 1024
        output_filename = filename + ".encrypted"
        filesize = str(os.path.getsize(filename)).zfill(16)
        nonce = get_random_bytes(16)

        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

        with open(filename, 'rb') as infile:
            with open(output_filename, 'wb') as outfile:
                outfile.write(filesize.encode('utf-8'))
                outfile.write(nonce)

                while True:
                    chunk = infile.read(chunk_size)

                    if len(chunk) == 0:
                        break

                    ciphertext, tag = cipher.encrypt_and_digest(chunk, AES.block_size)
                    outfile.write(ciphertext)

        return output_filename


class AsyncEncrypt:

    def encrypt_key(self,user,aes_key):

        public_key = RSA.importKey(user.pubKey)

        encrypted_aes_key = public_key.encrypt(aes_key,None )

        return encrypted_aes_key


from Crypto.Cipher import AES
from Crypto.PublicKey import RSA


class SyncDecrypt:

    def decrypt(self, filename, key, nonce):
        # Load the ciphertext and tag from the encrypted file
        with open(filename, 'rb') as f:
            ciphertext = f.read()
            tag = f.read(16)  # 16-byte (128-bit) tag

        # Decrypt the ciphertext using AES in EAX mode
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        # Save the decrypted file to disk
        with open('decrypted_file.pdf', 'wb') as f:
            f.write(plaintext)


class AsyncDecrypt:

    def decrypt_key(self, user, encrypted):
        private_key = RSA.importKey(user.pubKey)
        aes_key = private_key.decrypt(encrypted)
        return aes_key
