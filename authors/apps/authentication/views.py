import json
import os
import re
from datetime import datetime, timedelta

import django
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import IntegrityError
from django.template import context
from django.template.loader import get_template, render_to_string
from requests.exceptions import HTTPError

import jwt
from authors.apps.authentication.validations import UserValidation
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework import generics, status
from rest_framework.generics import (CreateAPIView, GenericAPIView,
                                     RetrieveUpdateAPIView, UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView, status
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import AuthForbidden, AuthTokenError, MissingBackend
from social_django.utils import load_backend, load_strategy

from .backends import GetAuthentication, JWTokens
from .messages import error_msg, success_msg
from .models import User
from .renderers import UserJSONRenderer
from .serializers import (LoginSerializer, RegistrationSerializer,
                          ResetPasswordSerializer,
                          SocialSignInSignOutSerializer, UserSerializer)
from .utils import status_codes, swagger_body
from .validations import UserValidation


class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    swagger_schema = SwaggerAutoSchema
    # the line above simply sets the swagger schema to be applied in this
    # class.
    # here, we're comfortable using the one defined in settings.py, which
    # currently,
    # is set to the default that ships with drf_yasg.

    # lets override some properties of the the default schema with our own
    # values
    @swagger_auto_schema(
        request_body=swagger_body(prefix="user", fields=(
            'email', 'username', 'password')),
        responses=status_codes(codes=(201, 400))
    )
    def post(self, request):
        """
            POST /users/
        """
        user = request.data.get('user', {})
        url = request.data.get('site')
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        payload = {'email': serializer.data.get("email")}
        token = jwt.encode(payload, os.getenv("SECRET_KEY"),
                           algorithm='HS256').decode()
        from_mail, to_mail = os.getenv(
            "DEFAULT_FROM_EMAIL"), serializer.data.get("email")
        subject = "Account Verification"
        site_url = "http://"+get_current_site(request).domain
        email_url = url if url else site_url
        link_url = email_url + "/verify/{}".format(token)
        print(link_url)
        html_page = render_to_string(
            "email_verification.html",
            context={"link": link_url,
                     "user_name": serializer.data.get("username")
                     }
        )
        send_mail(subject, "Verification mail", from_mail, [
                  to_mail], fail_silently=False, html_message=html_page)
        return Response({
            "message": success_msg['email_verify'],
            "username": serializer.data['username'],
            "email": serializer.data['email']
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer
    # Notice here that we do not call `serializer.save()` like we did for
    # the registration endpoint. This is because we don't actually have
    # anything to save. Instead, the `validate` method on our serializer
    # handles everything we need.
    swagger_schema = SwaggerAutoSchema

    # lets override some properties of the the default schema with our own
    # values
    @swagger_auto_schema(
        request_body=swagger_body(prefix="user", fields=('email', 'password')),
        responses=status_codes(codes=(200, 400))
    )
    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    swagger_schema = SwaggerAutoSchema

    @swagger_auto_schema(responses=status_codes(codes=(200, 400)))
    def get(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # lets override some properties of the the default schema with our own
    # values
    @swagger_auto_schema(
        request_body=swagger_body(prefix="user", fields=(
            'email', 'username', 'password')),
        responses=status_codes(codes=(201, 400)))
    def put(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyAPIView(GenericAPIView):
    """Verify endpoint holder"""
    serializer_class = UserSerializer
    swagger_schema = SwaggerAutoSchema

    # lets override some properties of the the default schema with our own
    # values
    @swagger_auto_schema(
        responses=status_codes(codes=(200, 404))
    )
    def get(self, request, token):
        """
            GET /verify/
        """
        serializer = self.serializer_class()
        email = jwt.decode(token, os.getenv("SECRET_KEY"))["email"]
        user = User.objects.get(email=email)
        if user:
            user.is_confirmed = True
            user.save()
            token = JWTokens.create_token(self, user)
            return Response({
                "message": "Email Successfully Confirmed",
                'email': user.email,
                'username': user.username,
                'token': token
            }, status=status.HTTP_200_OK
            )
        else:
            return Response({
                "message": "No user of that email"
            }, status=status.HTTP_404_NOT_FOUND)


class PasswordResetRequestAPIView(GenericAPIView):
    """Sends Password reset link to email """
    serializer_class = ResetPasswordSerializer
    swagger_schema = SwaggerAutoSchema

    # lets override some properties of the the default schema with our own
    # values
    @swagger_auto_schema(
        request_body=swagger_body(prefix="user", fields=(
            'email',)),
        responses=status_codes(codes=(200, 400))
    )
    def post(self, request):
        user_data = request.data
        email = user_data['email']
        request_site = request.data.get("site")

        # confirms if an eamil has been provided
        # if email is not given then an error message is thrown
        if not email.strip():
            return Response({
                'message': error_msg['no_email'],
            },
                status=status.HTTP_400_BAD_REQUEST)
        elif re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email) is None:
            return Response({
                'message': error_msg['email_format']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Confirms if a user with the given email actually exists
        # If user exists then the user instance is returned
        # the user instance is used to generate a token
        # a response is given with the email and the generated token
        elif User.objects.filter(email=email).exists():
            # fetch username using the email
            username = User.objects.all().filter(email=email).first()

            payload = {
                'email': email,
                "iat": datetime.now(),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, os.getenv("SECRET_KEY"),
                               algorithm='HS256').decode()

            # format the email
            host = request.get_host()
            protocol = request.scheme
            base_url = '/api/v1/users/password_reset/'
            reset_link = ""
            if request_site:
                reset_link = request_site + "/reset-password/" + token
            else:
                reset_link = protocol + '://' + host + base_url + token
            print("reset>>>>>>"+reset_link)
            subject = "Password Reset for Authors Haven Web Portal account"
            message = render_to_string(
                'request_password_reset.html', {
                    'email': email,
                    'token': token,
                    'username': str(username).capitalize(),
                    'link': reset_link
                })
            to_email = email
            from_email = os.getenv("DEFAULT_FROM_EMAIL")
            send_mail(
                subject,
                message,
                from_email, [
                    to_email,
                ],
                html_message=message,
                fail_silently=False)
            message = {
                'Message': success_msg['request_success'],
                'Token': token
            }
            return Response(message, status=status.HTTP_200_OK)

        # If user does not exist then an error is thrown to the user
        return Response({
            'message': error_msg['unregistered_email']},
            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(UpdateAPIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    swagger_schema = SwaggerAutoSchema

    # lets override some properties of the the default schema with our own
    # values
    @swagger_auto_schema(
        request_body=swagger_body(prefix="user", fields=(
            'password',)),
        responses=status_codes(codes=(200, 400)))
    def patch(self, request, token, **kwargs):
        # decode the token
        decoded = GetAuthentication.decode_jwt_token(token)
        # use the email to find decode the user instance
        user = User.objects.get(email=decoded['email'])
        # get the password that the user is keying in
        password = request.data['user']['password']
        # now we validate the password
        UserValidation.valid_password(self, password)
        # save the password after we have validated it
        self.serializer_class.update(
            None,
            user,
            {
                "password": password
            }
        )
        # Alert the user that the user has completed the password request
        return Response(
            {"message": success_msg["pwd_changed"]},
            status=status.HTTP_200_OK)

    # by dafault, swagger generates schemas for all endpoints available in
    # class based views
    # in this case, UpdateAPIView, has PATCH and PUT endpoints
    # setting auto_schema to None prevents this(PUT) endpoint from being
    # included in the swagger docs
    @swagger_auto_schema(auto_schema=None)
    def put(self):
        """
        Does nothing at the moment.

        It's here for the sake of swagger :-)
        """
        pass


class SocialSignInSignOut(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialSignInSignOutSerializer

    def post(self, request, *args, **kwargs):
        """ interrupt social_auth authentication pipeline"""
        # pass the request to serializer to make it a python object
        # serializer also catches errors of blank request objects
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.data.get('provider', None)
        strategy = load_strategy(request)  # creates the app instance

        if request.user.is_anonymous:  # make sure the user is not anonymous
            user = None
        else:
            user = request.user

        try:
            # load backend with strategy and provider from settings(AUTHENTICATION_BACKENDS)
            backend = load_backend(
                strategy=strategy, name=provider, redirect_uri=None)

        except MissingBackend as error:

            return Response({
                "errors": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # check type of oauth provide e.g facebook is BaseOAuth2 twitter is BaseOAuth1
            if isinstance(backend, BaseOAuth1):
                # oath1 passes access token and secret
                access_token = {
                    "oauth_token": serializer.data.get('access_token'),
                    "oauth_token_secret": serializer.data.get('access_token_secret'),
                }

            elif isinstance(backend, BaseOAuth2):
                # oauth2 only has access token
                access_token = serializer.data.get('access_token')

        except HTTPError as error:
            return Response({
                "error": {
                    "access_token": "invalid token",
                    "details": str(error)
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        except AuthTokenError as error:
            return Response({
                "error": "invalid credentials",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # authenticate the current user
            # social pipeline associate by email handles already associated exception
            authenticated_user = backend.do_auth(access_token, user=user)

        except HTTPError as error:
            # catch any error as a result of the authentication
            return Response({
                "error": "Http Error",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        except AuthForbidden as error:
            return Response({
                "error": "invalid token",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        if authenticated_user and authenticated_user.is_active:
            # Check if the user you intend to authenticate is active
            token = JWTokens.create_token(self, authenticated_user)
            headers = self.get_success_headers(serializer.data)
            response = {"email": authenticated_user.email,
                        "username": authenticated_user.username,
                        "token": token}

            return Response(response, status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            return Response({"errors": "Could not authenticate"},
                            status=status.HTTP_400_BAD_REQUEST)
