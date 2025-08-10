import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from accounts.models import User
from accounts.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestUserModel:
    """
    Test User Model

    Methods:
        test_create_writer_or_reader_user(): Test creating writer or reader user
        test_create_admin_user(): Test creating admin user.
        test_default_user_type(): Test default user type.
        test_username_uniqueness(): Test username uniqueness.
        test_invalid_user_type(): Test invalid user type.
        test_user_type_is_required_field(): Test user type is in REQUIRED_FIELDS.
    """

    def test_create_writer_or_reader_user(self):
        """
        Test creating writer or reader user
        """

        user = UserFactory(
            username="testuser",
            email="testuser@test.com",
            user_type=User.WRITER_OR_READER_USER
        )

        assert user.username == "testuser"
        assert user.email == "testuser@test.com"
        assert user.user_type == User.WRITER_OR_READER_USER

    def test_create_admin_user(self):
        """
        Test creating admin user
        """

        user = UserFactory(
            username="adminuser",
            email="adminuser@test.com",
            user_type=User.ADMIN_USER
        )

        assert user.username == "adminuser"
        assert user.email == "adminuser@test.com"
        assert user.user_type == User.ADMIN_USER

    def test_default_user_type(self):
        """
        Test default user type
        """

        user = User.objects.create(
            username="testuser2",
            email="testuser2@test.com",
        )
        assert user.user_type == User.WRITER_OR_READER_USER

    def test_username_uniqueness(self):
        """
        Test username uniqueness when provided
        """

        UserFactory(
            email='user1@example.com',
            user_type=User.WRITER_OR_READER_USER,
            username='test_user'
        )
        with pytest.raises((ValidationError, IntegrityError)):
            UserFactory(
                email='user2@example.com',
                user_type=User.WRITER_OR_READER_USER,
                password='testpass123',
                username='test_user',
            )

    def test_invalid_user_type(self):
        """
        Test that invalid user type throws error
        """

        with pytest.raises(ValidationError):
            user = UserFactory.build(
                email='invalid@test.com',
                user_type=3,
                password='ptest'
            )
            user.full_clean()

    def test_user_type_is_required_field(self):
        """
        Test REQUIRED_FIELDS contains user_type
        """

        assert 'user_type' in User.REQUIRED_FIELDS
