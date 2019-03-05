from rest_framework.exceptions import NotFound
from .models import Comments
from authors.apps.articles.models import Article
from ..authentication.messages import error_msg


class Utils:
    """
        Utilities class to check if the article and comment exists

    """

    def check_article(self, slug):
        # check if article exists
        try:
            article = Article.objects.get(slug=slug)
            return article
        except Article.DoesNotExist:
            raise NotFound(
                {"error": error_msg["no_slug"]})

    def check_comment(self, id):
        # check if Comment exists
        try:
            comment = Comments.objects.get(pk=id)
            return comment
        except Comments.DoesNotExist:
            raise NotFound(
                {"error": error_msg["no_comment"]})
