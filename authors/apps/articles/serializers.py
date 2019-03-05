import re
import math
import datetime as dt

from django.core.exceptions import ValidationError

from authors.apps.like_dislike.serializers import PreferenceSerializer
from authors.apps.authentication.messages import statusmessage
from authors.apps.like_dislike.models import LikeDislike
from rest_framework import serializers
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType

from authors.apps.authentication.serializers import RegistrationSerializer
from .messages import error_msgs
from .models import Article, Tags
from ..authentication.serializers import RegistrationSerializer
from .messages import error_msgs
from ..rating.models import Rating
from django.db.models import Avg
from authors.apps.articles.relations import TagsRelation


class ArticleSerializer(serializers.ModelSerializer):
    """
        Article model serializers
    """
    author = RegistrationSerializer(many=False, read_only=True, required=False)
    image_path = serializers.CharField(required=False, default=None)
    title = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    tags = TagsRelation(many=True, required=False)
    like_count = serializers.SerializerMethodField(read_only=True)
    dislike_count = serializers.SerializerMethodField(read_only=True)
    like_status = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    my_rating = serializers.SerializerMethodField(read_only=True)
    read_time = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = "__all__"

    def get_read_time(self, instance):
        """
            Here we get the body of the article instance we want to create
            Then we check if the body has words
            We then check the length of the words
            Then we divide the length with 200
            Then we stringify the output to get it in a time format
        """
        body = instance.body
        matching_words = re.findall(r'\w+', body)
        count = len(matching_words)
        read_per_min = math.ceil(count/200.0)
        read_time = str(dt.timedelta(minutes=read_per_min))
        return read_time

    def create_slug(self, title):
        """
            Create a slag
        """
        a_slug = slugify(title)
        origin = 1
        unique_slug = a_slug
        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(a_slug, origin)
            origin += 1
        slug = unique_slug
        return slug

    def get_like_count(self, obj):
        """ Return the number of likes"""

        return obj.prefs.count('likes')

    def get_dislike_count(self, obj):
        """Return the nimber of dislikes"""

        return obj.prefs.count('dislikes')

    def get_like_status(self, obj):
        """Get my preference"""
        user = self.context['request'].user
        content_type = ContentType.objects.get_for_model(
            obj)
        try:
            item = LikeDislike.objects.get(
                content_type=content_type, object_id=obj.id, user=user)
            return statusmessage['Like'] if int(item.pref) == 1 else statusmessage['Dislike']
        except Exception as e:
            if e.__class__.__name__ == "DoesNotExist":
                return statusmessage['Null']

    def get_rating(self, obj):
        """
            Get article rating.
        """
        average = Rating.objects.filter(
            article__pk=obj.pk).aggregate(Avg('your_rating'))

        if average['your_rating__avg'] is None:
            average_rating = 0
            return average_rating

        return average['your_rating__avg']

    def get_my_rating(self, obj):
        """
            Get my article rating.
        """
        user = self.context['request'].user
        try:
            current_rating = Rating.objects.get(
                user=user, article=obj).your_rating
            return (current_rating)
        except Exception as e:
            if e.__class__.__name__ == "DoesNotExist":
                return statusmessage['Null']


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('tag',)

    def to_representation(self, instance):
        return instance.tag
