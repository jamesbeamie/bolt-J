import os
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from authors.apps.authentication.messages import error_msg, success_msg

class TestUserFollow(APITestCase):
    """This class tests for user follow and unfollow"""
    def setUp(self):
        self.register_url = reverse("auth:register")
        self.login_uri = reverse('auth:login')
        self.valid_user_credentials = {
            "user": {
                "username":"wachira",
                "email":"ewachira254@gmail.com",
                "password":"Wachira254"
            }
        }
        self.valid_user2_credentials = {
            "user": {
                "username":"kerubo",
                "email":"kerubo@gmail.com",
                "password":"Wachira254"
            }
        }
    def user_login(self):
        self.client.post(
                self.register_url,
                self.valid_user_credentials,
                    format="json"
        )
        response = self.client.post(
            self.login_uri,
            data=self.valid_user_credentials,
            format="json"
        ) 
        token = response.data['token']
        return token
    def user2_login(self):
        self.client.post(
                self.register_url,
                self.valid_user2_credentials,
                format="json"
        )
        response = self.client.post(
            self.login_uri,
            data=self.valid_user2_credentials,
            format="json"
        ) 
        token = response.data['token']
        return token

    def follow(self):
        self.user_login()
        token = self.user2_login()
        follow_url = reverse('profile:follow', kwargs={'username': 'wachira'})
        response = self.client.post(follow_url, HTTP_AUTHORIZATION='Bearer ' + token, format='json')
        return response
    
    def test_follow(self):
        response = self.follow()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.data[1]['message'],
                      success_msg['success_followed'])

    def test_unfollow(self):
        self.follow()
        token = self.user2_login()
        follow_url = reverse('profile:follow', kwargs={'username': 'wachira'})
        response = self.client.post(follow_url, HTTP_AUTHORIZATION='Bearer ' + token, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.data[1]['message'],
                      success_msg['success_unfollowed'])

    def test_follow_self(self):
        token  = self.user_login()
        follow_url = reverse('profile:follow', kwargs={'username': 'wachira'})
        response = self.client.post(follow_url, HTTP_AUTHORIZATION='Bearer ' + token, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['message'],
                      error_msg['cannot_followself'])


    def test_get_all_followers(self):
        self.follow()
        token  = self.user_login()
        followers_url = reverse('profile:followers', kwargs={'username': 'wachira'})
        response = self.client.get(followers_url, HTTP_AUTHORIZATION='Bearer ' + token, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data[1]['message'],
                      success_msg['user_followers'])

    def test_get_all_following(self):
        self.follow()
        token  = self.user_login()
        following_url = reverse('profile:following', kwargs={'username': 'wachira'})
        response = self.client.get(following_url, HTTP_AUTHORIZATION='Bearer ' + token, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data[1]['message'],
                      success_msg['user_following'])

