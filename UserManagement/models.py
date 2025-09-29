from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import Group, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Custom encryption manager for secure field storage"""

    @staticmethod
    def get_encryption_key():
        """Get or generate encryption key from Django secret key"""
        # Use Django's SECRET_KEY as base for encryption key
        secret = settings.SECRET_KEY.encode('utf-8')
        salt = b'django_vault_salt_2024'  # Fixed salt for consistency

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret))
        return key

    @staticmethod
    def encrypt_data(plaintext):
        """Encrypt plaintext data"""
        if not plaintext:
            return None

        key = EncryptionManager.get_encryption_key()
        fernet = Fernet(key)

        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        encrypted = fernet.encrypt(plaintext)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    @staticmethod
    def decrypt_data(encrypted_data):
        """Decrypt encrypted data"""
        if not encrypted_data:
            return None

        try:
            key = EncryptionManager.get_encryption_key()
            fernet = Fernet(key)

            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception:
            return None


class EncryptedTextField(models.TextField):
    """Custom encrypted text field"""

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return EncryptionManager.decrypt_data(value)

    def to_python(self, value):
        if isinstance(value, str) and value:
            # If it looks like encrypted data, decrypt it
            if value.startswith('gAAAAA'):  # Fernet tokens start with this
                return EncryptionManager.decrypt_data(value)
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return EncryptionManager.encrypt_data(value)


# Create your models here.
class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['role'] = UserGroups.authority
        user = self._create_user(email, password, True, True, **extra_fields)
        return user


class UserGroups:
    authority = 1
    logistics = 2
    shipper = 3

    ROLES = (
        (authority, "Authority"),
        (logistics, "Logistics"),
        (shipper, "Shipper")
    )

    ROLES_Map = ("Authority", "Logistics", "Shipper")

    def get_permission_group(self, role: int):
        if role == self.authority:
            return Group.objects.get_or_create('Authority')

        if role == self.logistics:
            return Group.objects.get_or_create('Logistics')

        if role == self.shipper:
            return Group.objects.get_or_create('Shipper')
        return None


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="Email", max_length=254, unique=True)
    name = models.CharField(verbose_name="Name", max_length=254, null=True, blank=True)
    country = models.CharField(verbose_name="Country", max_length=25, null=False, )
    phone_no = models.CharField(verbose_name="Phone:", max_length=12, null=False, )
    role = models.PositiveSmallIntegerField(verbose_name="Role", choices=UserGroups.ROLES, default=UserGroups.shipper)
    port = models.CharField(verbose_name="Port",max_length=40,null=True)

    # RSA Key Storage for Enhanced Encryption
    public_key_pem = models.TextField(verbose_name="Public Key (PEM)", null=True, blank=True,
                                     help_text="RSA public key in PEM format")
    private_key_vault_id = models.CharField(verbose_name="Private Key Vault ID", max_length=100,
                                          null=True, blank=True,
                                          help_text="Reference ID for private key stored in crypto vault")
    key_generated_at = models.DateTimeField(verbose_name="Key Generation Date", null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    PASSWORD_FIELD = 'password'
    REQUIRED_FIELDS = ['country', 'name', 'phone_no', 'password']

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % self.pk

    def generate_rsa_keys(self):
        """Generate new RSA key pair for the user"""
        from Cryptography.Encryption import RSAKeyManager
        from django.utils import timezone
        import uuid

        private_pem, public_pem = RSAKeyManager.generate_key_pair(2048)

        # Store public key directly in user model
        self.public_key_pem = public_pem
        self.key_generated_at = timezone.now()

        # Generate unique vault ID for private key storage
        vault_id = f"user_{self.id}_{uuid.uuid4().hex[:8]}"
        self.private_key_vault_id = vault_id

        # Store private key in secure vault
        UserPrivateKeyVault.objects.update_or_create(
            vault_id=vault_id,
            defaults={
                'user': self,
                'private_key_encrypted': private_pem
            }
        )

        return private_pem, public_pem

    def has_rsa_keys(self):
        """Check if user has RSA keys generated"""
        return bool(self.public_key_pem and self.private_key_vault_id)

    def get_public_key(self):
        """Get user's public key"""
        return self.public_key_pem

    def get_private_key(self):
        """Get user's private key from secure vault"""
        if self.private_key_vault_id:
            try:
                vault = UserPrivateKeyVault.objects.get(vault_id=self.private_key_vault_id)
                return vault.private_key_encrypted
            except UserPrivateKeyVault.DoesNotExist:
                pass
        return None


class UserPrivateKeyVault(models.Model):
    """Secure storage for user private keys using custom encryption"""
    vault_id = models.CharField(max_length=100, unique=True, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='private_key_vault')
    private_key_encrypted = EncryptedTextField(verbose_name="Encrypted Private Key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Private Key Vault"
        verbose_name_plural = "User Private Key Vaults"

    def __str__(self):
        return f"Private Key Vault for {self.user.email}"