from ..messages import success, statusmessage
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from authors.apps.articles.models import Article
from authors.apps.authentication.backends import JWTokens
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.comments.models import Comments


class LikeDislikeTest(APITestCase):
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
        self.article = Article.objects.create(
            image_path="dan",
            title="rick",
            body="morty",
            slug="riick",
            author_id=self.user.id
        )
        self.like_url = reverse("likes:article_like", kwargs={
                                "slug": self.article.slug})
        self.dislike_url = reverse(
            "likes:article_dislike", kwargs={"slug": self.article.slug})
        self.comment = Comments.objects.create(
            author_profile=self.user.profile,
            article=self.article,
            body="My first comment"
        )
        self.comment_like_url = reverse("likes:comment_like", kwargs={
            "slug": self.article.slug, "pk": self.comment.id})
        self.comment_dislike_url = reverse("likes:comment_dislike", kwargs={
            "slug": self.article.slug, "pk": self.comment.id})

    def test_like_article(self):
        """Test liking an article"""

        response = self.client.post(
            self.like_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Like'])
        self.assertEqual(response.data['status'], statusmessage['Like'])

    def test_dislike_article(self):
        """Test disliking an article"""

        response = self.client.post(
            self.dislike_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Dislike'])
        self.assertEqual(response.data['status'], statusmessage['Dislike'])

    def test_un_like_article(self):
        """
        Tests undoing a like.

        If another like request is sent to an already liked article,
        it should undo the like.
        """

        self.client.post(
            self.like_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.like_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Null'])
        self.assertEqual(response.data['status'], statusmessage['Null'])

    def test_un_dislike_article(self):
        """
        Tests undoing a dislike

        If another dislike request is sent to an already liked article,
        it should undo the previous dislike.
        """
        self.client.post(
            self.dislike_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.dislike_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Null'])
        self.assertEqual(response.data['status'], statusmessage['Null'])

    def test_unauthenticated_like_article(self):
        """
        Try liking without authentication

        """
        response = self.client.post(
            self.like_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')

    def test_like_comment(self):
        """Test liking an article"""

        response = self.client.post(
            self.comment_like_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Like'])
        self.assertEqual(response.data['status'], statusmessage['Like'])

    def test_dislike_comment(self):
        """Test disliking an article"""

        response = self.client.post(
            self.comment_dislike_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Dislike'])
        self.assertEqual(response.data['status'], statusmessage['Dislike'])

    def test_un_like_comment(self):
        """
        Tests undoing a like.

        If another like request is sent to an already liked article, it should undo the like.
        """

        self.client.post(
            self.comment_like_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.comment_like_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Null'])
        self.assertEqual(response.data['status'], statusmessage['Null'])

    def test_un_dislike_comment(self):
        """
        Tests undoing a dislike

        If another dislike request is sent to an already liked article, it should undo the previous dislike.
        """
        self.client.post(
            self.comment_dislike_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.comment_dislike_url, content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], success['Null'])
        self.assertEqual(response.data['status'], statusmessage['Null'])

    def test_unauthenticated_like_comment(self):
        """
        Try liking without authentication

        """
        response = self.client.post(
            self.comment_like_url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'], 'Authentication credentials were not provided.')

    def tearDown(self):
        """
        This method is run after each test.
        There's nothing to do for now
        """
        pass
