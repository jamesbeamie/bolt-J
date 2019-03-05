import os
from rest_framework_jwt.settings import api_settings
import datetime
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
secret_key = settings.SECRET_KEY

"""Configure JWT Here"""

class JWTokens(object):
    """
    Handle token generation

    """
    def create_token(self, user):
        """
        Create and return the user's JWT token

        """
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return token

    def encode_token(self, user):
        """
        This method gerate token by encoding registered user
        email address
        """
        payload = {
           'id': user,
           'iat': datetime.utcnow()
        }
        return jwt.encode(payload, secret_key).decode('UTF-8')


class GetAuthentication(TokenAuthentication):
    """
      To decode a token

    """
    def decode_jwt_token(token):
        try:
            user_info = jwt.decode(token, secret_key)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'Token expired, request another one')
        return user_info
