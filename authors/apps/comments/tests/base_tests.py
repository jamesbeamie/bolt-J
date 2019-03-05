from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from ..models import Article
from authors.apps.authentication.models import User
from django.template.defaultfilters import slugify


class TestBaseCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('auth:register')
        self.login_url = reverse('auth:login')
        self.create_list_article_url = reverse('articles:articles')

        self.test_user1 = {
            'user': {
                'email': 'james@gmail.com',
                'password': 'TestUser123'
            }}

        self.article = {
            "title": "Its a test article",
            "body": "Its a test article body",
            "description": "hello"

        }

        self.comment = {
            "comment": {
                "body": "This is a test comment body."
            }
        }

        self.update_comment = {
            "comment": {
                "body": "This is a test update comment body."
            }
        }

        self.test_user = User.objects.create_user(
            username="jamess",
            email="james@gmail.com",
            password="TestUser123")

    def login_user(self):
        response = self.client.post(self.login_url,
                                    self.test_user1,
                                    format='json')
        token = response.data['token']
        return token

    def create_article(self):
        token = self.login_user()
        response = self.client.post(self.create_list_article_url,
                                    self.article,
                                    HTTP_AUTHORIZATION="Bearer " + token,
                                    format='json')
        slug = response.data['slug']
        return slug
