from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify

from authors.apps.authentication.models import User
from authors.apps.like_dislike.models import LikeDislike
from cloudinary.models import CloudinaryField


class Article(models.Model):
    """
        Each Article model schema
    """
    image_path = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(db_index=True, max_length=255)
    body = models.CharField(db_index=True, max_length=8055)
    tags = models.ManyToManyField('articles.Tags')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourites = models.BooleanField(default=False)
    author = models.ForeignKey(
        User, related_name="author", on_delete=models.CASCADE)
    prefs = GenericRelation(LikeDislike, related_query_name='articles')

    objects = models.Manager()


class Tags(models.Model):
    tag = models.CharField(max_length=120)

    def __str__(self):
        return self.tag
