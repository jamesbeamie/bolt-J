from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status


class UserLoginTest(APITestCase):
    """
            Holds test for handling login
    """

    def setUp(self):
        """Setup method"""
        self.client = APIClient()
        self.registration_uri = reverse('auth:register')
        self.login_uri = reverse('auth:login')
        self.valid_user_credentials = {
            "user": {
                "username":"Wachira",
                "email":"ewachira254@gmail.com",
                "password":"@Wachira254"
            }
        }
        self.valid_login_data = {
            "user": {
                "email": "ewachira254@gmail.com",
                "password": "@Wachira254"
            }
        }
        self.pwd_missing_special_char = {
            "user": {
                "email": "ewwachira254@gmail.com",
                "password": "wachira254"
            }
        }
        self.pwd_missing_caps = {
            "user": {
                "email": "ewwachira254@gmail.com",
                "password": "@wachira254"
            }
        }

        self.pwd_missing_number = {
            "user": {
                "email": "ewwachira254@gmail.com",
                "password": "@wachiratesh"
            }
        }
        self.short_pwd = {
            "user": {
                "email": "ewwachira254@gmail.com",
                "password": "@Wa254"
            }
        }

    def test_valid_login(self):
        """Test login a valid user"""
        self.client.post(
                        self.registration_uri,
                        self.valid_user_credentials,
                        format="json"
        )

        response = self.client.post(
            self.login_uri,
            data=self.valid_login_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_special_char(self):
        """check for special character in password"""
        self.client.post(
            self.registration_uri,
            self.valid_user_credentials,
            format="json"
        )

        response = self.client.post(
            self.login_uri,
            self.pwd_missing_special_char,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_caps(self):
        """Test for capital letter in password"""
        self.client.post(
            self.registration_uri,
            self.valid_user_credentials,
            format="json"
        )

        response = self.client.post(
            self.login_uri,
            self.pwd_missing_caps,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_number(self):
        """Test atleast a number in password"""
        self.client.post(
            self.registration_uri,
            self.valid_user_credentials,
            format="json"
        )

        response = self.client.post(
            self.login_uri,
            self.pwd_missing_number,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_length(self):
        """Test for atleast 8 characteer password"""
        self.client.post(
            self.registration_uri,
            self.valid_user_credentials,
            format="json"
        )

        response = self.client.post(
            self.login_uri,
            self.short_pwd,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)
