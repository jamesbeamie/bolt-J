from rest_framework import serializers
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q

from authors.apps.favorite.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    """
        Favorite model serializer
    """
    article_url = serializers.CharField(required=True)

    class Meta:
        model = Favorite
        fields = "__all__"

    def create_article_url(self, request, article_slug):
        """
            Create the article url 
        """
        base_url = "http://" + get_current_site(request).domain + "/"
        article_url = base_url + "api/v1/articles/" + article_slug + "/"
        return article_url

    def check_article(self, slug, user_id):
        """
            Check if that article was favorited
        """
        favorite = Favorite.objects.filter(
            Q(article_slug=slug) & Q(user=user_id)
        )
        if favorite:
            return False
        else:
            return True

    def get_that_one_favorite(self, slug, user_id):
        """
            Get one article from favorites
        """
        favorite = Favorite.objects.filter(
            Q(article_slug=slug) & Q(user=user_id)
        )
        if favorite:
            return favorite
        else:
            return False

    def get_all_favorites(self, user):
        """
            Get all articles
        """
        favorites = Favorite.objects.filter(user=user).all()
        return favorites
