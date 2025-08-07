import factory
from faker import Faker

from accounts.models import User

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """
    A factory for creating instances of User model for testing.
    This factory provides default values for creating a User model  instance,
    with auto-generated fields username and email.

    Attributes:
        username (str): A unique username for the user, automatically generated using a sequence.
        email (str): An email address for the user, automatically generated using username value.
        user_type (int): The  user type which can be 'ADMIN_USER' or 'WRITER_OR_READER_USER'.
        is_verified (bool): True if the user is verified, False otherwise.
        created_at (datetime): The date and time the user was created, generated using Faker.
        updated_at (datetime): The date and time the user was last updated, generated using Faker.
    """

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")

    user_type = factory.Iterator([User.ADMIN_USER, User.WRITER_OR_READER_USER])

    is_verified = factory.Faker('boolean')

    created_at = factory.LazyAttribute(faker.date_time_this_year)
    updated_at = factory.LazyAttribute(faker.date_time_this_year)
