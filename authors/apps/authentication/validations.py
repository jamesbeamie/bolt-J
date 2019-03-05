import re
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

# Local imports
from .messages import error_msg
from .models import User


class UserValidation(object):
    """
    This is to validate user input on registration and login and return
    descriptive validation error messages
    """

    def re_search(self, data, errors):
        for key, val in errors.items():
            if re.search(key, data) is None:
                raise ValidationError(error_msg[val])
        return True

    def valid_email(self, email=None):
        """
        Function to validate the user email on registration
        """
        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            raise ValidationError(error_msg['usedemail'])
        elif re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email) is None:
            raise ValidationError(error_msg['email_format'])
        return True

    def valid_username(self, username=None):
        """
        Function to validate the username on registration
        """

        errors = {
            '[A-Za-z]': 'no_letter',
            '[A-Za-z]|[0-9]': 'special_character',
        }
        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            raise ValidationError(error_msg['usedname'])
        elif len(username) < 3:
            raise ValidationError(error_msg['shortname'])
        UserValidation.re_search(self, username, errors)
        return True

    def valid_password(self, password=None):
        """
        Function to validate the user password on registration
        """
        errors = {
            '[0-9]': 'number_in_pwd',
            '[a-z]': 'letter_in_pwd',
            '[A-Z]': 'caps_in_pwd'
        }
        if len(password) < 8:
            raise ValidationError(error_msg['short_pwd'])
        UserValidation.re_search(self, password, errors)
        return True

    def valid_login_email(self, email=None):
        """
        Function to validate the user email on registration
        """
        user_qs = User.objects.filter(email=email)
        if re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email) is None:
            raise ValidationError(error_msg['email_format'])
        elif not user_qs.exists():
            raise ValidationError(error_msg['unregistered_email'])
        return True
