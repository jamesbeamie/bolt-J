import os

from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status


class EmailVerificationTest(APITestCase):
    """
        Email verification test holder
    """

    def setUp(self):
        """
            setup method
        """
        self.client = APIClient()
        self.registration_url = reverse('auth:register')
        self.login_url = reverse("auth:login")
        self.registration_data = {
            "user": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "@Test254"
            }
        }
        self.login_data = {
            "user": {
                "email": "test@gmail.com",
                "password": "@Test254"
            }
        }

    def test_email_verification(self):
        """Test email verification"""
        mail.send_mail(
            'Account verification', 'Here is the message.',
            os.getenv("EMAIL_HOST_USER"), ['test@gmail.com'],
            fail_silently=False
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].body)

    def test_login_enverified_mail_verification(self):
        """
            Test email verification
        """
        self.client.post(
            self.registration_url,
            data=self.registration_data,
            format="json"
        )
        response = self.client.post(
            self.login_url,
            data=self.login_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data)
