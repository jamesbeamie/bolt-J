from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..messages import error_msg, success_msg
from django.core import mail


class TestResetPassword(TestCase):
    """Test data"""

    def setUp(self):
        client = Client()
        self.register_url = reverse("auth:register")

    # Data with valid user credentials
        self.valid_user_credentials = {
            "user": {
                "username": "Alpha",
                "email": "alphaandela@gmail.com",
                "password": "@Alpha254"
            }
        }
        self.user_email = [
            {
                "email": ""
                },
            {
                    "email": "newuser@gmail.com"
                },
            {
                    "email": "alpha@andela"
                },
             {
                    "email": "alphaandela@gmail.com"
                },
        ]

    def user_registration(self):
        """Register a User"""
        response = self.client.post(
            self.register_url,
            self.valid_user_credentials,
            content_type='application/json'
        )
        return response

    def get_email(self):
        """Get email of the registered user"""
        email = self.user_registration().data['email']
        mail = {
                "email": email
            }
        return mail

    def submit_email(self, data):
        return self.client.post(
            reverse("auth:reset_request"),
            data,
            content_type='application/json')

    def test_request_reset_without_email(self):
        """Test request password reset without an email"""
        response = self.submit_email(self.user_email[0])
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data['message'],
            error_msg['no_email'])

    def test_reset_request_with_unregistered_email(self):
        """Test request password reset with unregistered user email"""
        response = self.submit_email(self.user_email[1])

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.json(),
            {"message": error_msg['unregistered_email']})

    def test_if_message_sent_to_registered_user(self):
        """Test request password reset with registered user email"""
        response = self.submit_email(self.get_email())
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

        self.assertEqual(
            response.data['Message'],
            success_msg['request_success'])

        self.assertEqual(len(mail.outbox), 2)
        self.assertNotIn("token", response.data)

    def test_user_inputs_an_email_with_invalid_email(self):
        """Test if a user tries to input an email without @"""
        response = self.submit_email(self.user_email[2])
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(len(mail.outbox), 0)

        self.assertEqual(
            response.data['message'],
            error_msg['email_format']
        )

    def test_user_email_without_com_at_the_end(self):
        """Test is user tries to input an email without com"""
        response = self.submit_email(self.user_email[2])
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(len(mail.outbox), 0)

        self.assertEqual(
            response.data['message'],
            error_msg['email_format']
        )

    def test_user_email_without_dot_at_the_end(self):
        """ Test is user tries to input an email without (.) """
        response = self.submit_email(self.user_email[2])
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(len(mail.outbox), 0)

        self.assertEqual(
            response.data['message'],
            error_msg['email_format']
        )

    def test_user_sings_in_with(self):
        response = self.submit_email(self.get_email())
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

        self.assertEqual(
            response.data['Message'],
            success_msg['request_success'])
