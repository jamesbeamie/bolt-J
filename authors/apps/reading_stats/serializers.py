from rest_framework import serializers

from .models import ReadStats


class ReadStatsSerializers(serializers.ModelSerializer):
    """"
       Serializer class for our ReadStats model
    """

    article = serializers.SerializerMethodField()

    class Meta:
        model = ReadStats

        fields = '__all__'

    def get_article(self, stats):
        return {
            "article": stats.article.title,
            "slug": stats.article.slug
        }
