from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with additional fields.

    This model represents users with features beyond Django's default user model.
    It uses email as the primary identifier instead of username.

    Attributes:
        user_type (PositiveSmallIntegerField): User role classification with choices:
            - ADMIN_USER (1): Administrator with full privileges
            - WRITER_OR_READER_USER (2): Standard user with limited permissions
        username (CharField): Optional username field.
        email (EmailField): Primary user identifier, used for authentication
        is_verified (BooleanField): Flag indicating email verification status
        created_at (DateTimeField): Timestamp of user creation (auto-set)
        updated_at (DateTimeField): Timestamp of last update (auto-updated)

    Methods:
        __str__(): Returns the email address as string representation
    """

    ADMIN_USER = 1
    ADMIN_USER_NAME = 'admin'
    WRITER_OR_READER_USER = 2
    WRITER_OR_READER_NAME = 'writer or reader'

    USER_TYPE_CHOICES = (
        (ADMIN_USER, ADMIN_USER_NAME),
        (WRITER_OR_READER_USER, WRITER_OR_READER_NAME),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES,
                                                 default=2,
                                                 )
    username = models.CharField(max_length=255,
                                unique=True,
                                null=True,
                                blank=True,
                                db_index=True,
                                )
    email = models.EmailField(max_length=255,
                              unique=True,
                              null=True,
                              blank=True,
                              db_index=True,
                              )
    is_verified = models.BooleanField(default=False,
                                      )
    created_at = models.DateTimeField(auto_now_add=True,
                                      )
    updated_at = models.DateTimeField(auto_now=True,
                                      )
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ["user_type"]

    def __str__(self):
        return self.email
