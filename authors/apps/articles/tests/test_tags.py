from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.template.defaultfilters import slugify
import json
from ..models import Article
from ...authentication.models import User
from authors.apps.authentication.backends import JWTokens
from ..messages import error_msgs, success_msg
from rest_framework import status


class ArticleTestCase(APITestCase):
    """
        Tags endpoints test
    """

    def setUp(self):
        """
            Setup method
        """
        self.all_article_url = reverse("articles:articles")
        self.tag_url = reverse("articles:tags")
        self.post_tag_url = reverse("articles:specific_article",
                                    kwargs={"slug": "this-is-a-blog"})

        self.invalid_tag_url = reverse("articles:specific_article",
                                       kwargs={"slug": "this-is"})

        self.client = APIClient()

        self.tag_body = {
            "tags": ["this a tag"]
        }

        self.invalid_tag_body = {
            "tags": ["this a tag!"]
        }

        self.edit_tag_body = {
            "tags": [""]
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

    def test_post_tag(self):
        response = self.client.put(
            self.post_tag_url,
            self.tag_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_remove_tag(self):
        response = self.client.put(
            self.post_tag_url,
            self.edit_tag_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_post_tag(self):
        response = self.client.put(
            self.post_tag_url,
            self.tag_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            format="json"
        )
        self.assertEqual(response.data['message'],
                         error_msgs['article_owner_error'])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_tag(self):
        response = self.client.put(
            self.post_tag_url,
            self.invalid_tag_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            format="json"
        )
        self.assertEqual(response.data['tags']['message'],
                         error_msgs['invalid_tag'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_empty_tags(self):
        response = self.client.get(
            self.tag_url,
            format="json"
        )
        self.assertEqual(response.data['message'],
                         error_msgs['tags_not_found'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_unavailable_article(self):
        response = self.client.put(
            self.invalid_tag_url,
            self.tag_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            format="json"
        )
        self.assertEqual(response.data['detail'],
                         "Not found.")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
