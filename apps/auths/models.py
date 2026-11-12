from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import BooleanField, CharField, EmailField


# Create your models here.
class CustomUserManager(BaseUserManager):
    """Manager: knows how to create users correctly."""

    def create_user(
            self,
            email:str,
            full_name: str,
            password: str | None = None,
            **extra_fields: Any,
    ) -> "CustomUser":
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email = email, full_name = full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(
            self, 
            email: str,
            full_name:str,
            password: str | None = None,
            **extra_fields: Any,
    ) -> "CustomUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, full_name, password, **extra_fields)




class CustomUser(AbstractBaseUser, PermissionsMixin):
    """User who logs in with meail."""

    EMAIL_MAX_LEN = 254
    FULL_NAME_MAX_LEN = 150

    email = EmailField(
        max_length=EMAIL_MAX_LEN,
        unique=True,
    )

    full_name = CharField(
        max_length=FULL_NAME_MAX_LEN,
    )

    is_active=BooleanField(default=True)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self) ->str:
        return self.email