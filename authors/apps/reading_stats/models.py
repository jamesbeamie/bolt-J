from django.db import models

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article


class ReadStats(models.Model):
    """
        The model for user read starts
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=False, blank=False)
    article_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.article.title
