from django.urls import reverse
from rest_framework import status
from django.test import TestCase, Client
import json
from rest_framework.authtoken.models import Token
from ..messages import error_msgs, success_msg
from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.authentication.backends import JWTokens


class TestArticleRating(TestCase):
    def setUp(self):
        self.client = Client()
        self.email_url = reverse("articles:email_share",
                                 kwargs={"slug": "this-is-a-blog"})
        self.facebook_url = reverse("articles:facebook_share",
                                    kwargs={"slug": "this-is-a-blog"})
        self.twitter_url = reverse("articles:twitter_share",
                                   kwargs={"slug": "this-is-a-blog"})

        self.wrong_email_url = reverse("articles:email_share",
                                       kwargs={"slug": "this-is-a"})
        self.wrong_facebook_url = reverse("articles:facebook_share",
                                          kwargs={"slug": "this-is-a"})
        self.wrong_twitter_url = reverse("articles:twitter_share",
                                         kwargs={"slug": "this-is-a"})

        self.wrong_url = url = reverse("rating:rate",
                                       kwargs={"slug": "this-is-a"})

        self.email_body = {
            'email': "ewachira254@gmail.com"
        }
        self.no_email_body = {
            'email': ""
        }
        self.invalid_email_body = {
            'email': "ewachira254gmail.com"
        }

        self.create_user_1 = User.objects.create_user(
            username="wachira",
            email="ewachira254@gmail.com",
            password="@Wachira254"
        )
        self.token_user_1 = JWTokens.create_token(
            self, user=self.create_user_1)

        self.create_user_2 = User.objects.create_user(
            username="bolton",
            email="bolton@gmail.com",
            password="@bolton254"
        )
        self.token_user_2 = JWTokens.create_token(
            self, user=self.create_user_2)

        self.correct_article = Article.objects.create(
            author_id=self.create_user_1.id,
            image_path="...",
            title="This is a blog",
            body="This is a body",
            slug="this-is-a-blog"
        )

    def test_share_via_email(self):
        response = self.client.post(
            self.email_url,
            self.email_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         success_msg['share_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)

    def test_share_via_facebook(self):
        response = self.client.post(
            self.facebook_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         success_msg['share_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)

    def test_share_via_twitter(self):
        response = self.client.post(
            self.twitter_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         success_msg['share_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)

    def test_unauthorized_share_via_email(self):
        response = self.client.post(
            self.email_url,
            self.email_body,
            content_type='application/json'
        )

        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_share_via_facebook(self):
        response = self.client.post(
            self.facebook_url,
            content_type='application/json'
        )

        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_share_via_twitter(self):
        response = self.client.post(
            self.twitter_url,
            content_type='application/json'
        )

        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_share_via_email_without_receivers_email(self):
        response = self.client.post(
            self.email_url,
            self.no_email_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         error_msgs['no_email'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_via_email_with_invalid_receivers_email(self):
        response = self.client.post(
            self.email_url,
            self.invalid_email_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         error_msgs['email_format'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_via_email_nonexisting_article(self):
        response = self.client.post(
            self.wrong_email_url,
            self.email_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         error_msgs['not_found'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_via_facebook_nonexisting_article(self):
        response = self.client.post(
            self.wrong_facebook_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         error_msgs['not_found'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_via_twitter_nonexisting_article(self):
        response = self.client.post(
            self.wrong_twitter_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         error_msgs['not_found'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_via_email_by_others(self):
        response = self.client.post(
            self.email_url,
            self.email_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         success_msg['share_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)

    def test_share_via_facebook_by_others(self):
        response = self.client.post(
            self.facebook_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         success_msg['share_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)

    def test_share_via_twitter_by_others(self):
        response = self.client.post(
            self.twitter_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )

        self.assertEqual(response.data['message'],
                         success_msg['share_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shared_link", response.data)
