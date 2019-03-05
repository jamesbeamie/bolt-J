from rest_framework.test import APIClient, APITestCase
from django.urls import reverse

from authors.apps.articles.models import Article
from authors.apps.favorite.serializers import FavoriteSerializer


class FavoriteTestCase(APITestCase):
    """
        Favorites test object holder
    """

    def setUp(self):
        """
            Setup method
        """
        self.client = APIClient()
        # Define payloads
        self.article_data = {
            "image-path": "....",
            "body": "this is a test article body",
            "title": "this is a test article title"
        }
        self.user_data = {
            "user": {
                "username": "test",
                "email": "test@gmail.com",
                "password": "Test254@"
            }
        }
        # Define urls
        self.login_url = reverse("auth:login")
        self.signup_url = reverse("auth:register")
        self.get_all_favorites = reverse("fav:favorites")
        self.wrong_slug_favorite_url = reverse(
            "fav:favorite-article", kwargs={
                "slug":"nothing-else-my-test"
            }
        )
        self.wrong_slug_unfavorite_url = reverse(
            "fav:unfavorite-article", kwargs={
                "slug":"nothing-else-my-test"
            }
        )
        self.articles = reverse(
            "articles:articles"
        )


    def login_user(self):
        self.client.post(
            self.signup_url,
            data=self.user_data,
            format="json"
        )
        response = self.client.post(
            self.login_url,
            data=self.user_data,
            format="json"
        )
        return response.data['token']

    def create_article(self, token):
        """
            Create an article
        """
        response = self.client.post(
            self.articles, 
            data=self.article_data,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        return response

    def test_favoriting_an_article(self):
        """
            test making an article favorite
        """
        token = self.login_user()
        slug = self.create_article(token).data['slug']
        self.favorite_url = reverse(
            "fav:favorite-article", kwargs={"slug": slug})
        response = self.client.post(
            self.favorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 200)

    def test_unfavoriting_an_article(self):
        """
            test removing a article from favorites
        """
        token = self.login_user()
        slug = self.create_article(token).data['slug']
        self.favorite_url = reverse(
            "fav:favorite-article", kwargs={"slug": slug})
        self.unfavorite_url = reverse(
            "fav:unfavorite-article", kwargs={"slug": slug})
        self.client.post(
            self.favorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        response = self.client.post(
            self.unfavorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['message'])

    def test_favoriting_a_not_found_article(self):
        """
            test making an article favorite
        """
        token = self.login_user()
        response = self.client.post(
            self.wrong_slug_favorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.data['detail'])

    def test_unfavoriting_a_not_found_article(self):
        """
            test making an article favorite
        """
        token = self.login_user()
        response = self.client.post(
            self.wrong_slug_unfavorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.data['message'])
    
    def test_favoriting_a_favorited_article(self):
        """
            test favoriting a favorited article
        """
        token = self.login_user()
        slug = self.create_article(token).data['slug']
        self.favorite_url = reverse(
            "fav:favorite-article", kwargs={"slug": slug})
        self.client.post(
            self.favorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        response = self.client.post(
            self.favorite_url,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEqual(response.status_code, 406)
        self.assertTrue(response.data['message'])

    def test_getting_all_favorites(self):
        """
            Test fetching all favorites
        """
        token = self.login_user()
        response = self.client.get(
            self.articles,
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token)
        )

        self.assertEqual(response.status_code, 200)
