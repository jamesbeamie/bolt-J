import os
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.test import TestCase
from rest_framework import status


class SocialAuthTest(APITestCase):
    """This class tests the social login and social signup"""

    def setUp(self):
        self.client = APIClient()
        self.namespace = 'auth'

        self. social_auth_url = reverse(
            self.namespace + ':social_signin_signup')
        self.test_social_body = {
            "provider": "facebook",
            "access_token": os.getenv('FB_TOKEN')
        }
        self.test_twitter_body = {
            "provider": "twitter",
            "access_token": os.getenv('TWITTER_ACCESS_TOKEN'),
            "access_token_secret": os.getenv('TWITTER_TOKEN_SECRET')
        }
        self.test_invalid_provider = {
            "provider": "invalid-provider",
            "access_token": os.getenv('GOOGLE_TOKEN')
        }
        self.test_invalid_token = {
            "provider": "google-oauth2",
            "access_token": "invalid-token"
        }


    # def test_social_auth_api(self):
    #     facebookresponse = self.client.post(self.social_auth_url, self.test_social_body, format='json')
    #     twitterresponse = self.client.post(self.social_auth_url, self.test_twitter_body, format='json')
    #     googleresponse =self.client.post(self.social_auth_url, self.test_google_body, format='json')
    #     invalidtoken = self.client.post(self.social_auth_url, self.test_invalid_token, format= 'json')
    #     invalidprovider = self.client.post(self.social_auth_url, self.test_invalid_provider, format='json')

    #     # self.assertEqual(facebookresponse.status_code, status.HTTP_201_CREATED)
    #     # self.assertEqual(twitterresponse.status_code, status.HTTP_201_CREATED)
    #     # self.assertEqual(googleresponse.status_code, status.HTTP_201_CREATED)
    #     # self.assertTrue(invalidtoken.status_code, status.HTTP_400_BAD_REQUEST)
    #     # self.assertTrue(invalidprovider.status_code, status.HTTP_400_BAD_REQUEST)

   
