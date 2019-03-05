from rest_framework import serializers
from .messages import error_msg
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Rating
from django.db.models import Avg


class RatingSerializer(serializers.ModelSerializer):
    """
        Rating model serializers
    """
    max_rate = 5
    min_rate = 1
    your_rating = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(
                min_rate,
                message=error_msg['min_rate']
            ),
            MaxValueValidator(
                max_rate,
                message=error_msg['max_rate']
            )
        ],
        error_messages={
            'required': error_msg['no_rating']
        }
    )
    article = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    rate_count = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        """
            Returns rating average
        """
        average = Rating.objects.filter(
            article=obj.article.id).aggregate(Avg('your_rating'))
        return average['your_rating__avg']

    def get_article(self, obj):
        """
            Gets article slug
        """
        return obj.article.slug

    def get_rate_count(self, obj):
        """
            Gets article rate count
        """
        count = Rating.objects.filter(
            article=obj.article.id).count()
        return count

    class Meta:
        model = Rating
        fields = ('article', 'average_rating', 'rate_count', 'your_rating')
