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

                    ciphertext, tag = cipher.encrypt_and_digest(pad(chunk, AES.block_size))
                    outfile.write(ciphertext)

        return output_filename


class AsyncEncrypt:

    def encrypt_key(self,user,aes_key):

        public_key = RSA.importKey(user.pubKey)

        encrypted_aes_key = public_key.encrypt(aes_key,None )

        return encrypted_aes_key


