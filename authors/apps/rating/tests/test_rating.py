from django.urls import reverse
from rest_framework import status
from django.test import TestCase, Client
import json
from rest_framework.authtoken.models import Token
from ..messages import error_msg, success_msg
from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.authentication.backends import JWTokens


class TestArticleRating(TestCase):
    def setUp(self):
        self.client = Client()
        self.correct_url = reverse("rating:rate",
                                   kwargs={"slug": "this-is-a-blog"})
        self.wrong_url = url = reverse("rating:rate",
                                       kwargs={"slug": "this-is-a"})
        self.rating_body = {
            'your_rating': 5
        }

        self.invalid_rating_body = {
            'your_rating': "d"
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

    def test_post_rating(self):
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # Get Rating when logged in
        response = self.client.get(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         success_msg['retrive_success'])

        # Get Rating when NOT logged  in
        response = self.client.get(self.correct_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['your_rating'], error_msg['no_login'])

    def test_rate_own_article(self):
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )
        self.assertEqual(
            response.json().get('errors').get('message'),
            error_msg['own_rating'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_article_not_existing(self):
        response = self.client.post(
            self.wrong_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )

        self.assertEqual(
            response.json().get('errors').get('message'),
            error_msg['not_found'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_using_wrong_value(self):
        response = self.client.post(
            self.correct_url,
            self.invalid_rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )

        self.assertEqual(
            response.json().get('errors').get('your_rating'),
            ["A valid integer is required."])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_with_less_value(self):
        self.less_value = {'your_rating': 0}
        response = self.client.post(
            self.correct_url,
            self.less_value,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.json().get('errors').get('your_rating'),
            [error_msg['min_rate']])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_with_more_value(self):
        self.less_value = {'your_rating': 6}
        response = self.client.post(
            self.correct_url,
            self.less_value,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.json().get('errors').get('your_rating'),
            [error_msg['max_rate']])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_with_no_value(self):
        response = self.client.post(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )

        self.assertEqual(
            response.json().get('errors').get('your_rating'),
            [error_msg['no_rating']])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_when_not_logged_in(self):
        response = self.client.post(self.correct_url,
                                    self.rating_body,
                                    content_type='application/json'
                                    )
        self.assertEqual(response.json().get('detail'), error_msg['no_token'])
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rating_again_updates_previous_value(self):
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])
        self.assertEqual(response.data['message'], success_msg['rate_success'])

        self.rating = {
            'your_rating': 4
        }
        response = self.client.post(
            self.correct_url,
            self.rating,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])
        self.assertEqual(response.data['message'], success_msg['rate_success'])

    def test_get_rating(self):
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])
        self.assertEqual(response.data['message'], success_msg['rate_success'])

        response = self.client.get(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("your_rating", response.data['data'])
        self.assertEqual(response.data['message'],
                         success_msg['retrive_success'])

    def test_get_rating_of_non_existing_article(self):
        response = self.client.get(
            self.wrong_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2)

        self.assertEqual(response.json().get('errors').get('message'),
                         error_msg['not_found'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_rate_with_no_rating(self):
        response = self.client.get(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("your_rating", response.data)
        self.assertEqual(response.data['average_rating'], 0)
        self.assertEqual(response.data['your_rating'],
                         error_msg['rating_not_found'])

    def test_get_rated_article_when_not_logged(self):
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])
        self.assertEqual(response.data['message'], success_msg['rate_success'])

        response = self.client.get(self.correct_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 5)
        self.assertEqual(response.data['your_rating'], error_msg['no_login'])

    def test_get_unrated_article_when_not_logged(self):
        response = self.client.get(self.correct_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 0)
        self.assertEqual(response.data['your_rating'], error_msg['no_login'])

    def test_user_can_delete_rating(self):
        # rate article
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # delete rate article
        response = self.client.delete(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.data['message'],
            success_msg['delete_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_rating_twice(self):
        # rate article
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # delete rate article
        response = self.client.delete(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.data['message'],
            success_msg['delete_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # delete same rate again
        response = self.client.delete(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.json().get('rating'),
            error_msg['rating_not_found'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_someone_else_rating(self):
        # rate article
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertIn(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # delete rate article
        response = self.client.delete(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_1,
            content_type='application/json'
        )

        self.assertEqual(
            response.json().get('errors').get('message'),
            error_msg['no_delete'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_delete_with_no_rating(self):
        response = self.client.delete(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.json().get('rating'),
            error_msg['rating_not_found'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_article_not_existing(self):

        response = self.client.delete(
            self.wrong_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.json().get('errors').get('message'),
            error_msg['not_found'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_when_not_logged(self):
        response = self.client.delete(self.correct_url,
                                      content_type='application/json'
                                      )
        self.assertEqual(response.json().get('detail'), error_msg['no_token'])
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_deleted_rating(self):
        # rate article
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertIn(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # delete rate article
        response = self.client.delete(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertEqual(
            response.data['message'],
            success_msg['delete_success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get deleted rate
        response = self.client.get(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("your_rating", response.data)
        self.assertEqual(response.data['average_rating'], 0)
        self.assertEqual(response.data['your_rating'],
                         error_msg['rating_not_found'])

    def test_average_rating(self):
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertIn(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # Get Average rating
        response = self.client.get(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get(
            'data').get('average_rating'), 5.0)
        self.assertIn("average_rating", response.json().get('data'))
        self.assertEqual(response.data['message'],
                         success_msg['retrive_success'])

        self.rating_body = {
            'your_rating': 4
        }

        # Change the rate
        response = self.client.post(
            self.correct_url,
            self.rating_body,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2,
            content_type='application/json'
        )
        self.assertIn(response.data['message'], success_msg['rate_success'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("your_rating", response.data['data'])

        # Get Average rating again
        response = self.client.get(
            self.correct_url,
            HTTP_AUTHORIZATION='Bearer ' + self.token_user_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get(
            'data').get('average_rating'), 4.0)
        self.assertIn("average_rating", response.json().get('data'))
        self.assertEqual(response.data['message'],
                         success_msg['retrive_success'])