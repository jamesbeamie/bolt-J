# System libraries
import json

# Third Party Libraries
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status


class UserRegistrationTest(APITestCase):
    """
            Holds all user registration
    """

    def setUp(self):
        """The setup method"""
        self.register_url = reverse("auth:register")
        self.client = APIClient()

        # Define the json data
        # Data with valid user credentials
        self.valid_user_credentials = {
            "user": {
                "username": "Wachira",
                "email": "ewachira254@gmail.com",
                "password": "@Wachira254"
            }
        }
        # Data lacking a field <username>
        self.missing_field_credentials = {
            "user": {
                "username": "",
                "email": "ewachira254@gmail.com",
                "password": "@Wachira254"
            }
        }
        # Data lacking with no username
        self.none_field_credentials = {
            "user": {
                "email": "ewachira254@gmail.com",
                "password": "@Wachira254"
            }
        }
        # Data lacking with no email
        self.none_field_credentials_2 = {
            "user": {
                "username": "isasnack",
                "password": "@Wachira254"
            }
        }
        # Data with invalid data <password>
        self.invalid_field_credentials = {
            "user": {
                "username": "Wachira",
                "email": "ewachira254@gmail.com",
                "password": "123456"
            }
        }

        self.invalid_username = {
            "user": {
                "username": "W",
                "email": "ewachira254@gmail.com",
                "password": "123456"
            }
        }

        self.short_password = {
            "user": {
                "username": "Wachira",
                "email": "ewachira254@gmail.com",
                "password": "AS"
            }
        }

        self.invalid_email = {
            "user": {
                "username": "Wachira",
                "email": "invalid.com",
                "password": "AS"
            }
        }

    def test_user_registration_missing_username(self):
        """Test the user registration"""
        response = self.client.post(
            self.register_url,
            self.none_field_credentials,
            format="json"
        )
        data = response.data
        self.assertTrue(data['errors']['username'])

    def test_user_registration_missing_email(self):
        """Test the user registration"""
        response = self.client.post(
            self.register_url,
            self.none_field_credentials_2,
            format="json"
        )
        data = response.data
        self.assertTrue(data['errors']['email'])
