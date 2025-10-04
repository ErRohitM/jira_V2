from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from common.models import BaseModels

class UserTypeChoices(models.TextChoices):
    OWNER = "Owner", _("Owner")
    MANAGER = "Manager", _("Manager")
    MEMBER = "Member", _("Member")

def assign_to_user_group(user, user_type):
    try:
        # Define group and permission based on user_type
        # group_name = 'Staff' if user_type == UserTypeChoices.STAFF else 'Admin'
        if user_type == UserTypeChoices.OWNER:
            group_name = 'Owner'
        elif user_type == UserTypeChoices.MANAGER:
            group_name = 'Manager'
        else:
            group_name = 'Member'

        # Get or create the group and permission
        user_group, group_created = Group.objects.get_or_create(name=group_name)

        # Add the group and permission to the user
        if not user.groups.filter(name=group_name).exists():
            user.groups.add(user_group)

    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(f"Error fetching objects: {e}")
    except ValidationError as e:
        raise ValueError(f"{e} Validation Failed")

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, user_type, password=None, **extra_fields):
        """Create and return a user with an email, first name, last name, user type, and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        assign_to_user_group(user, user_type)
        return user

    def create_superuser(self, email, first_name, last_name, user_type, password=None, **extra_fields):
        """Create and return a superuser with an email, first name, last name, user type, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, user_type, password=password, **extra_fields)

class BaseUser(AbstractBaseUser, BaseModels, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255, blank=True)

    # Add these fields to meet Django's requirements
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    user_type = models.CharField(max_length=255, choices=UserTypeChoices, default=UserTypeChoices.MEMBER)

    # Specify that 'username' is not used
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# class PasswordReset(models.Model):
#     email = models.EmailField()
#     token = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#
# class UserCredentialsSentMailLogs(BaseModels):
#     mailing_user = models.CharField(max_length=255, null=False, blank=False)
#     user_mail_id = models.EmailField()