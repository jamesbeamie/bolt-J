from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.template.defaultfilters import slugify

from ..models import Article
from ...authentication.models import User
from authors.apps.authentication.messages import read_stats_message


class ArticleTestCase(APITestCase):
    """
        Article endpoints test
    """

    def setUp(self):
        """
            Setup method
        """
        # All articles urls
        self.all_article_url = reverse("articles:articles")
        self.login_url = reverse("auth:login")
        self.register = reverse("auth:register")
        self.read_stats = reverse("read:user_read_stats")
        self.client = APIClient()
        self.valid_article_data = {
            "article": {
                "image_path": "......",
                "title": "Its a test article",
                "body": "Its a test article body"
            }
        }

        self.invalid_article_data = {
            "image_path": "......",
            "title": "Its a test article",
            "body": ""
        }

        self.update_article_data = {
            "image_path": "......",
            "title": "Its a test article",
            "body": "ajdlkjasl;dkfjalk;sdjf"
        }

        self.user_data = {
            "user": {
                "username": "test",
                "email": "test@fmail.com",
                "password": "Test@254"
            }
        }

    def login(self, data):
        """
            Login a registered user
        """
        # Register a user
        self.client.post(
            self.register,
            data=data,
            format="json"
        )
        response = self.client.post(
            self.login_url,
            data=data,
            format="json"
        )
        return response.data['token']

    def get_slug_from_title(self, title):
        """
            Get slug
        """
        specific_article_url = reverse(
            "articles:specific_article",
            kwargs={
                "slug": slugify(title)
            }
        )
        return specific_article_url

    def get_slug(self, title):
        """
            Get slug
        """
        slug = slugify(title)
        return slug

    def create_article(self, data):
        """
            Create an article
        """
        article = Article(
            image_path=data['image_path'],
            slug=slugify(data['title']),
            title=data['title'],
            body=data['body'],
            author_id=1
        )
        article.save()

    def test_get_all_artcles(self):
        """
            Test GET /api/v1/articles/
        """
        response = self.client.get(
            '/api/v1/articles/',
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_get_one_article(self):
        """
            Test GET /api/v1/article/<slug>/
        """
        token = self.login(self.user_data)
        self.create_article(self.valid_article_data['article'])
        url = self.get_slug_from_title(
            self.valid_article_data['article']['title'])
        response = self.client.get(
            url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 200)

    def test_get_stat(self):
        """
            Test GET /api/v1/article/<slug>/
        """
        token = self.login(self.user_data)
        self.create_article(self.valid_article_data['article'])
        response = self.client.get(
            self.read_stats,
            content_type='application/json',
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 200)

    def test_read(self):
        """
            Test reading an article that doesnot exist
        """
        token = self.login(self.user_data)
        self.create_article(self.valid_article_data['article'])
        slug = "its-a-test-article"
        response = self.client.get(
            reverse("read:article_read", kwargs={
            "slug":slug
        }),
            content_type='application/json',
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(response.data['message'],
                      read_stats_message['read_error'])

    def test_read_new(self):
        """
            
        """
        token = self.login(self.user_data)
        self.create_article(self.valid_article_data['article'])
        slug = self.get_slug(self.valid_article_data['article']['title'])
        response = self.client.get(
            reverse("read:article_read", kwargs={
            "slug":slug
        }),
            content_type='application/json',
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(response.data['message'],
                      read_stats_message['read_error'])


    def test_remove_one_article(self):
        """
            Test DELETE /api/v1/article/<slug>/
        """
        token = self.login(self.user_data)
        self.create_article(self.valid_article_data['article'])
        url = self.get_slug_from_title(
            self.valid_article_data['article']['title'])
        response = self.client.delete(
            url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 403)

    def test_create_an_article_with_wrong_values(self):
        """
            BAd request testing
        """
        token = self.login(self.user_data)
        reponse = self.client.post(
            self.all_article_url,
            data=self.invalid_article_data,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(reponse.status_code, 400)

    def test_not_found_article(self):
        """
            Not found request
        """
        token = self.login(self.user_data)
        url = self.get_slug_from_title("just a wrong title for a wrong slug")
        response = self.client.get(
            url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_not_found_article(self):
        """
            Not found request
        """
        token = self.login(self.user_data)
        url = self.get_slug_from_title("just a wrong title for a wrong slug")
        response = self.client.delete(
            url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)

    def test_update_not_found_article(self):
        """
            Not found request
        """
        token = self.login(self.user_data)
        url = self.get_slug_from_title("just a wrong title for a wrong slug")
        response = self.client.put(
            url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)

    def test_update_uauthorized_article_creation(self):
        """
            PUT /api/v1/articles/<slug>/
        """
        token = self.login(self.user_data)
        self.create_article(self.valid_article_data['article'])
        url = self.get_slug_from_title(
            self.valid_article_data['article']['title'])
        response = self.client.put(
            url,
            data=self.update_article_data,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        """
            Teardown method
        """
        User.objects.all().delete()
        Article.objects.all().delete()
