from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import Group, PermissionsMixin
from django.db import models
from django.utils import timezone


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


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="Email", max_length=254, unique=True)
    name = models.CharField(verbose_name="Name", max_length=254, null=True, blank=True)
    country = models.CharField(verbose_name="Country", max_length=25, null=False, )
    phone_no = models.CharField(verbose_name="Phone:", max_length=12, null=False, )
    role = models.PositiveSmallIntegerField(verbose_name="Role", choices=UserGroups.ROLES, default=UserGroups.shipper)
    port = models.CharField(verbose_name="Port",max_length=40,null=True)
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



