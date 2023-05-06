from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import User


class TestMovieNightUserManager(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.assertEqual(user.email, "testuser@test.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="superuser@test.com", password="superpassword"
        )
        self.assertEqual(superuser.email, "superuser@test.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="testpassword")

    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superuser@test.com", password="superpassword", is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superuser@test.com",
                password="superpassword",
                is_superuser=False,
            )


class TestUser(TestCase):
    def test_str_representation(self):
        user = User(email="testuser@test.com")
        self.assertEqual(str(user), "testuser@test.com")

    def test_email_uniqueness(self):
        User.objects.create_user(email="testuser@test.com", password="testpassword")

        with self.assertRaises(ValidationError):
            duplicate_user = User(email="testuser@test.com")
            duplicate_user.full_clean()
