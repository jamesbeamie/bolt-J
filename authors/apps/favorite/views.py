from rest_framework import status, exceptions
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import Response
from django.shortcuts import get_object_or_404

from authors.apps.favorite.serializers import FavoriteSerializer
from authors.apps.articles.models import Article
from authors.apps.favorite.models import Favorite
from authors.apps.favorite.messages import error_msgs, success_msg


class FavoriteAPIView(generics.CreateAPIView):
    """
        A user should be able to add an article to their favorites
    """
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug, *args, **kwargs):
        """
            PUT /api/v1/articles/<slug>/favorite/
        """
        article = get_object_or_404(Article.objects.all(), slug=slug)
        article_url = FavoriteSerializer().create_article_url(request, slug)
        user = request.user.id
        data = {
            "user": user,
            "article_url": article_url,
            "article_title":article.title,
            "article_slug":slug
        }
        serializer = FavoriteSerializer(
            data=data
        )
        if FavoriteSerializer().check_article(slug, user):
            serializer.is_valid()
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "message": error_msgs['article_favorited']
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

class UnfavoriteAPIView(generics.CreateAPIView):
    """
        A user should be able to remove articles from their favorites
    """
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug, *args, **kwargs):
        """
            POST /api/v1/articles/<slug>/unfavorite/
        """
        user = request.user.id
        favorite = FavoriteSerializer().get_that_one_favorite(slug, user)
        if favorite:
            favorite.delete()            
            return Response(
                {
                    "message":success_msg['favorite_deleted']
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "message":error_msgs['favorite_not_found']
                },
                status=status.HTTP_404_NOT_FOUND
            )

class GetOwnFavoritesAPIView(generics.ListAPIView):
    """
        A user should be able remove articles from their favorites
    """
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
            GET /api/v1/favorites/
        """
        user = request.user.id
        favorites = FavoriteSerializer().get_all_favorites(user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        