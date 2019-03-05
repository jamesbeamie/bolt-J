import os

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from authors.apps.authentication.validations import UserValidation


class ValidationTest(APITestCase):
    """
        Email verification test holder
    """

    def setUp(self):
        """
            setup method
        """
        self.email = "diana.kerubo@gmail.com"
        self.username = "Diana254"
        self.password = "@Diana254"

    def test_valid_email(self):
        """
            Test a valid mail
        """
        self.assertEqual(UserValidation().valid_email(email=self.email), True)

    def test_valid_username(self):
        """
            Test a valid username
        """
        self.assertEqual(UserValidation().valid_username(
            username=self.username), True)

    def test_valid_password(self):
        """
            Test a valid password
        """
        self.assertEqual(UserValidation().valid_password(
            password=self.password), True)
