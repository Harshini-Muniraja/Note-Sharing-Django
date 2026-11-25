from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationTests(TestCase):
    def test_register_saves_profile_fields_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "harshini",
                "first_name": "Harshini",
                "last_name": "M",
                "email": "harshini@example.com",
                "password1": "S3cure-Pass-9876",
                "password2": "S3cure-Pass-9876",
            },
        )
        self.assertRedirects(response, reverse("notes:my_notes"))
        user = User.objects.get(username="harshini")
        self.assertEqual(user.first_name, "Harshini")
        self.assertEqual(user.email, "harshini@example.com")
        self.assertTrue(user.check_password("S3cure-Pass-9876"))

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user("first", "same@example.com", "S3cure-Pass-9876")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "second",
                "first_name": "Second",
                "email": "SAME@example.com",
                "password1": "S3cure-Pass-9876",
                "password2": "S3cure-Pass-9876",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="second").exists())
