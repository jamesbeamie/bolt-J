from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from ..models import ReadStats
from authors.apps.articles.models import Article
from django.template.defaultfilters import slugify
from authors.apps.authentication.messages import read_stats_message


class ReadStatsTestCase(TestCase):

    def setUp(self):
        client = Client()
        self.login_url = reverse("auth:login")
        self.register_url = reverse("auth:register")
        self.read_stats = reverse("read:user_read_stats")
        self.all_article_url = reverse("articles:articles")

        self.valid_article_data = {
            "article": {
                "image_path": "",
                "title": "Its a test article",
                "body": "Its a test article body"
            }
        }

        self.valid_user_credentials = {
            "user": {
                "username": "Alpha",
                "email": "alphaandela@gmail.com",
                "password": "@Alpha254"
            }
        }

        self.user_credentials = {
            "user": {
                "username": "Alpha",
                "email": "alphaandela@gmail.com",
                "password": "@Alpha254"
            }
        }

        self.valid_article_data = {
            "article": {
                "image_path": "......",
                "title": "Its a test article",
                "body": "Its a test article body"
            }
        }

    def user_registration(self, data):
        # register a user
        response = self.client.post(
            self.register_url,
            self.valid_user_credentials,
            content_type='application/json'
        )
        return response

    def login(self, data):
        # login user
        response = self.client.post(
            self.login_url,
            self.valid_user_credentials,
            content_type='application/json'
        )
        return response

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

    # def test_create_article(self):
    #     """
    #         Create an article
    #     """
    #     self.user_registration(self.valid_user_credentials)
    #     token = self.login(self.valid_user_credentials).data['token']

    #     response = self.client.post(
    #         self.all_article_url,
    #         self.valid_article_data,
    #         format="json",
    #         HTTP_AUTHORIZATION="Bearer " + token
    #     )
    #     import pdb; pdb.set_trace()
    #     return response.data

    def test_user_read_starts(self):
        """
           test to get list of users read articles
        """
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        token = res.data['token']
        response = self.client.get(
            self.read_stats,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, 200)

    def test_read_error(self):
        """
        test response given to user
        """
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        slug = "slug"
        token = res.data['token']
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
    


    def test_user_start(self):
        """
            test length of data returned
        """
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        token = res.data['token']
        response = self.client.get(
            self.read_stats,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        data = response.data
        
        self.assertTrue(len(data) == 4)

    def test_user_results_with_no_read(self):
        """
            test length of result data returned
        """
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        token = res.data['token']
        response = self.client.get(
            self.read_stats,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        data = response.data
        self.assertTrue(len(data['results']) == 0)


    def test_user_read_article_that_doesnot_exist(self):
        """
            test if a user tires to read a non existent article        
        """
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        slug = "slug"
        token = res.data['token']
        response = self.client.get(
            "api/v1/read," + slug + "/",
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, 404)

    def test_stat_without_being_authenticated(self):
        """
        test to ensure authentication is required
        """
        self.login(self.valid_user_credentials)
        token = "new"
        response = self.client.get(
            self.read_stats,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, 401)
    
    def test_read_user_response(self):
        """
        test response given to user
        """
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        slug = "slug"
        token = res.data['token']
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

   
    
