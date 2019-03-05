from rest_framework.generics import (
    GenericAPIView
)
from .models import Article, Rating
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.exceptions import NotFound, ValidationError
from .serializers import RatingSerializer
from rest_framework.response import Response
from .messages import error_msg, success_msg
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from django.db.models import Avg


class RatingAPIView(GenericAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_article(self, slug):
        """
            Returns specific article using slug
        """
        article = Article.objects.all().filter(slug=slug).first()
        return article

    def get_rating(self, user, article):
        """
            Returns user article rating
        """
        try:
            return Rating.objects.get(user=user, article=article)
        except Rating.DoesNotExist:
            raise NotFound(detail={'rating': error_msg['rating_not_found']})

    def post(self, request, slug):
        """
            Posts a rate on an article
        """
        rating = request.data
        article = self.get_article(slug)

        # check if article exists
        if not article:
            raise ValidationError(
                detail={'message': error_msg['not_found']})

        # check owner of the article
        if article.author == request.user:
            raise ValidationError(
                detail={'message': error_msg['own_rating']})

        # updates a user's rating if it already exists
        try:
            # Update Rating if Exists
            current_rating = Rating.objects.get(
                user=request.user.id,
                article=article.id
            )
            serializer = self.serializer_class(current_rating, data=rating)
        except Rating.DoesNotExist:
            #  Create rating if not founds
            serializer = self.serializer_class(data=rating)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, article=article)

        return Response({
            'message': success_msg['rate_success'],
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        """
            Gets articles rates
        """
        article = self.get_article(slug)
        rating = None

        # check if article exists
        if not article:
            raise ValidationError(
                detail={'message': error_msg['not_found']})

        if request.user.is_authenticated:
            try:
                rating = Rating.objects.get(user=request.user, article=article)
            except Rating.DoesNotExist:
                pass

        if rating is None:
            avg = Rating.objects.filter(
                article=article).aggregate(Avg('your_rating'))

            average = avg['your_rating__avg']
            count = Rating.objects.filter(
                article=article.id).count()

            if avg['your_rating__avg'] is None:
                average = 0

            if request.user.is_authenticated:
                return Response({
                    'article': article.slug,
                    'average_rating': average,
                    'rate_count': count,
                    'your_rating': error_msg['rating_not_found']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'article': article.slug,
                    'average_rating': average,
                    'rate_count': count,
                    'your_rating': error_msg['no_login']
                }, status=status.HTTP_200_OK)

        serializer = self.serializer_class(rating)
        return Response({
            'message': success_msg['retrive_success'],
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        """
            Deletes a rating
        """
        article = self.get_article(slug)

        if request.user.is_authenticated:
            # check if article exists
            if not article:
                raise ValidationError(
                    detail={'message': error_msg['not_found']},)

            elif article.author != request.user:
                # get user rating and delete
                rating = self.get_rating(user=request.user, article=article)
                rating.delete()
                return Response(
                    {'message': success_msg['delete_success']},
                    status=status.HTTP_200_OK
                )
            else:
                raise ValidationError(
                    detail={'message': error_msg['no_delete']})
