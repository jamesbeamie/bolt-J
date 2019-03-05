from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.authentication.backends import JWTokens
from authors.apps.authentication.messages import error_msg, success_msg


from .base_tests import TestBaseCase
from rest_framework import status


class CommentsTests(TestBaseCase):
    """
    Comments test cases
    """

    def forbidden_403(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def ok_200(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def created_201(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_create_comment(self):
        """
        Test if authenticated users can create comments
        """
        token = self.login_user()
        slug = self.create_article()

        response = self.client.post(
            reverse('comments:comment', kwargs={'slug': slug}),
            self.comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_can_create_comment(self):
        """
        Test if unauthenticated users can create comments
        """

        slug = self.create_article()

        response = self.client.post(
            reverse('comments:comment', kwargs={'slug': slug}),
            self.comment,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_comments(self):
        """
        Test if authenticated users can create comments
        """
        token = self.login_user()
        slug = self.create_article()

        response = self.client.get(
            reverse('comments:comment', kwargs={'slug': slug}),
            self.comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_specific_comment(self):
        """
        Test if authenticated users can create comments
        """

        token = self.login_user()
        slug = self.create_article()
        response = self.client.post(
            reverse('comments:comment', kwargs={'slug': slug}),
            self.comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        comment_id = response.data.get('id')
        response = self.client.get(
            reverse('comments:specific_comment',
                    kwargs={"slug": slug, "id": comment_id}),
            self.comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        """
        Test if authenticated users can create comments
        """

        token = self.login_user()
        slug = self.create_article()
        response = self.client.post(
            reverse('comments:comment', kwargs={'slug': slug}),
            self.comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        comment_id = response.data.get('id')
        response = self.client.put(
            reverse('comments:specific_comment',
                    kwargs={"slug": slug, "id": comment_id}),
            self.update_comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment(self):
        """
        Test if authenticated users can create comments
        """

        token = self.login_user()
        slug = self.create_article()
        response = self.client.post(
            reverse('comments:comment', kwargs={'slug': slug}),
            self.comment,
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        comment_id = response.data.get('id')
        response = self.client.delete(
            reverse('comments:specific_comment',
                    kwargs={"slug": slug, "id": comment_id}),
            HTTP_AUTHORIZATION="Bearer " + token,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
