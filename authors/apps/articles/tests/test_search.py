from django.urls import reverse

from authors.apps.articles.models import Article, Tags
from authors.apps.authentication.backends import JWTokens
from authors.apps.authentication.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from ..messages import error_msgs
from ..serializers import ArticleSerializer


class CustomSearchTest(APITestCase):
    """
    Tests on liking and disliking articles

    """

    def setUp(self):
        """
        Set up initial values

        This is run before each test
        """

        self.client = APIClient()
        self.username = "dann"
        self.email = "dann@dan.com"
        self.password = "Qwertyuiop1"
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        self.user.is_confirmed = True
        self.token = JWTokens.create_token(self, user=self.user)
        self.title = 'rick'
        self.tag_body = {
            "tags": ["News"]
        }
        for i in range(10):
            article = Article.objects.create(
                image_path="dan",
                title=self.title,
                body="Lorem ipsum dolor sit amet, consectetur adipiscing elit,\
                 sed do eiusmod tempor incididunt ut labore et dolore magna \
                 aliqua. Ut enim ad minim veniam, quis nostrud exercitation \
                 ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                slug=ArticleSerializer.create_slug(self, self.title),
                author_id=self.user.id
            )
            self.add_tags(article.slug)
        self.articles = reverse("articles:search-articles")
        self.search_term = '?author=haha'

    def add_tags(self, slug):
        post_tag_url = reverse("articles:specific_article",
                               kwargs={"slug": slug})
        self.client.put(
            post_tag_url,
            self.tag_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token,
            format="json"
        )

    def test_get_all_articles(self):
        """
            Test GET /api/v1/articles
        """
        response = self.client.get(
            (self.articles),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

    def test_get_articles_by_author(self):
        """
            Test GET /api/v1/articles?author=dan
        """
        response = self.client.get(
            (self.articles + '?author=dan'),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertIn('dan', response.data[0].get('author').get('username'))

    def test_unavailable_author(self):
        """
            Test GET /api/v1/articles?author=false
        """
        response = self.client.get(
            (self.articles + '?author=false'),
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get('message'), error_msgs['not_found'])

    def test_search_title(self):
        """
            Test GET /api/v1/articles?title=rick
        """
        response = self.client.get(
            (self.articles + '?title=rick'),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertIn('rick', response.data[0].get('title'))

    def test_search_non_title(self):
        """
            Test GET /api/v1/articles?title=non-existent
        """
        response = self.client.get(
            (self.articles + '?title=non-existent'),
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get('message'), error_msgs['not_found'])

    def test_search_body(self):
        """
            Test GET /api/v1/articles?body=Lorem+ipsum
        """
        response = self.client.get(
            (self.articles + '?body=Lorem+ipsum'),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertIn('Lorem', response.data[0].get('body'))
        self.assertIn('ipsum', response.data[0].get('body'))

    def test_search_non_body(self):
        """
            Test GET /api/v1/articles?body=Hakuna
        """
        response = self.client.get(
            (self.articles + '?body=Hakuna'),
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get('message'), error_msgs['not_found'])

    def test_search_tags(self):
        """
            Test GET /api/v1/articles?tag=News
        """
        response = self.client.get(
            (self.articles + '?tag=News'),
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertTrue('News' in response.data[0].get('tags'))

    def test_search_non_tags(self):
        """
            Test GET /api/v1/articles?tag=none
        """
        response = self.client.get(
            (self.articles + '?tag=none'),
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get(
            'message'), error_msgs['not_found'])

    def tearDown(self):
        """
        This method is run after each test.
        There's nothing to do for now
        """
        pass
