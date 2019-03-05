from django.contrib.contenttypes.models import ContentType
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.authentication.messages import statusmessage
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.like_dislike.models import LikeDislike
from authors.apps.like_dislike.serializers import PreferenceSerializer
from authors.apps.profiles.serializers import UserProfileSerializer
from rest_framework import serializers
from .models import Comments


class CommentSerializer(serializers.ModelSerializer):
    """
       Serializer class for comments
    """
    author_profile = UserProfileSerializer(
        many=False, read_only=True, required=False)
    article = ArticleSerializer(read_only=True)
    like_count = serializers.SerializerMethodField(read_only=True)
    dislike_count = serializers.SerializerMethodField(read_only=True)
    like_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comments
        fields = ('article', 'id', 'created_at', 'updated_at',
                  'body', 'author_profile', 'like_count', 'dislike_count', 'like_status')

        read_only_fields = ('id', 'author_profile',
                            'created_at', 'updated_at', 'article')

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
            return statusmessage['Like'] if item.pref == 1 else statusmessage['Dislike']

        except Exception as e:
            if e.__class__.__name__ == "DoesNotExist":
                return statusmessage['Null']
