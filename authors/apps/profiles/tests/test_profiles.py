from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from ..models import Profile
from authors.apps.authentication.messages import error_msg, success_msg


class TestProfile(TestCase):
    """
    Check if profiles functionality is working as expected

    """
    def setUp(self):
        client = Client()
        self.login_url = reverse("auth:login")
        self.register_url = reverse("auth:register")
        self.profile_url = reverse("prof:authors_profile")

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

        self.update_profile = {
            'profile':
            {
                "bio": "i am a tech enthusiast",
                "image": "default.jpg",
                "company": "Andela",
                "location": "cape Town",
                "First_name": "John",
                "Last_name": "Doe"
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

    def test_model_auto_create_user_profile(self):
        # test profile gets created when user is registered
        initial_count = Profile.objects.count()
        self.user_registration(self.valid_user_credentials)
        new_count = Profile.objects.count()
        self.assertNotEqual(initial_count, new_count)

    def test_get_other_user_profile(self):
        # test user can see other users profile
        self.user_registration(self.valid_user_credentials)
        self.login(self.valid_user_credentials)
        res = self.login(self.valid_user_credentials)
        username = res.data['username']
        token = res.data['token']
        url = '/api/v1/profiles/' + username + '/'
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data[1]['message'],
                      success_msg['profil_success'])

    def test_user_can_view_their_profile(self):
        # user can view their profile
        self.user_registration(self.valid_user_credentials)
        self.user_registration(self.user_credentials)
        res = self.login(self.valid_user_credentials)
        token = res.data['token']
        url = '/api/v1/profiles/'
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data[1]['message'],
                      success_msg['profil_success'])

    def test_get_invalid_user_profile(self):
        # test to try and view profile of a user who doesnot exist
        self.user_registration(self.user_credentials)
        res = self.login(self.user_credentials)

        username = 'ruiru'
        token = res.data['token']
        url = '/api/v1/profiles/' + username + "/"
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(response.data['detail'], error_msg['profile_not_there'])

    def test_user_can_not_edit_other_users_profile(self):
        # user cannot edit other users profile
        self.user_registration(self.valid_user_credentials)
        self.user_registration(self.user_credentials)
        res = self.login(self.valid_user_credentials)
        username = 'tesh'
        token = res.data['token']
        url = '/api/v1/profiles/' + username + '/edit/'
        response = self.client.patch(
            url,
            self.update_profile,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(response.data['detail'],
                      error_msg['cannot_update_profile'])

    def test_user_can_update_their_profile(self):
        # user can edit their profile
        self.user_registration(self.valid_user_credentials)
        self.user_registration(self.user_credentials)
        res = self.login(self.valid_user_credentials)
        username = res.data['username']
        token = res.data['token']
        url = '/api/v1/profiles/' + username + '/edit/'
        response = self.client.patch(
            url,
            self.update_profile,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data[1]['message'],
                      success_msg['profil_update'])

    def test_user_cannot_view_profiles_if_not_logged_in(self):
        # user must be logged in to view profiles
        self.user_registration(self.valid_user_credentials)
        self.user_registration(self.user_credentials)
        res = self.login(self.valid_user_credentials)
        token = res.data['token']
        url = '/api/v1/profiles/'
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Token ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
