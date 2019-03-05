from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType

from django.db import models
from authors.apps.authentication.models import User
from django.db.models import Sum


class LikeDislikeManager(models.Manager):
    """"
    Manager to handle LikeDislikes objects
    """
    use_for_related_fields = True

    def count(self, param):
        """"
        Return the number of likes or dislikes
        """

        queryset = self.get_queryset()
        if param == 'likes':
            # return the count of records greater than 0
            return queryset.filter(pref="1").count()
        elif param == 'dislikes':
            # return the count of records less than 0
            return queryset.filter(pref="-1").count()


class LikeDislike(models.Model):
    """
    Likes and dislikes model
    """

    LIKE = 1
    DISLIKE = -1

    PREF = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )

    pref = models.CharField(verbose_name=("preference"),
                            choices=PREF, max_length=128)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()
