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
