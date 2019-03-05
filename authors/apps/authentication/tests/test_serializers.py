import os

from rest_framework.test import APITestCase

from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import RegistrationSerializer


class SerializerTest(APITestCase):
    """
        Email verification test holder
    """

    def setUp(self):
        """
            setup method
        """
        self.user_details = {
            "username": "Diana254",
            "email": "diana.kerubo@gmail.com",
            "password": "Diana254@"
        }
        self.serialized_data = {
            "username": "Diana254",
            "email": "diana.kerubo@gmail.com",
            "password": "Diana254@"
        }
        self.user = User.objects.create(**self.user_details)
        self.serializer = RegistrationSerializer(instance=self.user_details)

    def test_registration_serializer(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['email', 'username']))
