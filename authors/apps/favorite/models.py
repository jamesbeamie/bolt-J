from django.db import models
from cloudinary.models import CloudinaryField

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User


class Favorite(models.Model):
    """
        Favorite model
    """
    article_url = models.TextField(null=True)
    article_title = models.CharField(max_length=255, null=True)
    article_slug = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(
        User, related_name="favorites", on_delete=models.CASCADE)
    favorited_date = models.DateTimeField(auto_now_add=True)
