import datetime as dt
import json
import os
import random
import re
from datetime import datetime, timedelta

import django
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from authors.apps.authentication.utils import status_codes, swagger_body
from authors.apps.core.pagination import PaginateContent
from authors.apps.reading_stats.models import ReadStats
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework import exceptions, generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import Response

from .filters import ArticleFilter
from .messages import error_msgs, success_msg
from .models import Article, Tags, User
from .renderers import ArticleJSONRenderer
from .serializers import ArticleSerializer, TagSerializers


class ArticleAPIView(generics.ListCreateAPIView):
    """
        Article endpoints
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @swagger_auto_schema(
        request_body=swagger_body(prefix="article", fields=(
            'image_path', 'title', 'body')),
        responses=status_codes(codes=(201, 400))
    )
    def post(self, request):
        """
            POST /api/v1/articles/
        """
        permission_classes = (IsAuthenticated,)
        context = {"request": request}
        article = request.data.copy()
        article['slug'] = ArticleSerializer(
        ).create_slug(request.data['title'])
        serializer = self.serializer_class(data=article, context=context)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        """
            GET /api/v1/articles/
        """
        perform_pagination = PaginateContent()
        objs_per_page = perform_pagination.paginate_queryset(
            self.queryset, request)
        serializer = ArticleSerializer(
            objs_per_page,
            context={
                'request': request
            },
            many=True
        )
        return perform_pagination.get_paginated_response(serializer.data)


class SpecificArticle(generics.RetrieveUpdateDestroyAPIView):
    """
        Specific article endpoint class
    """
    serializer_class = ArticleSerializer

    def get(self, request, slug, *args, **kwargs):
        """
            GET /api/v1/articles/<slug>/
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise exceptions.NotFound({
                "message": error_msgs['not_found']
            })
        # this checks if an istance of read exists
        # if it doesn't then it creates a new one
        if request.user.id:
            if not ReadStats.objects.filter(user=request.user, article=article).exists():
                user_stat = ReadStats(
                    user=request.user,
                    article=article
                )
                user_stat.article_read = True
                user_stat.save()

        serializer = ArticleSerializer(
            article,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=200)

    def delete(self, request, slug, *args, **kwargs):
        """
            DELETE /api/v1/articles/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise exceptions.NotFound({
                "message": error_msgs['not_found']
            })
        if request.user.id != article.author_id:
            return Response({
                "message": error_msgs["article_owner_error"]
            }, status=403)
        else:
            article.delete()
            return Response({
                "article": success_msg['article_delete']
            }, status=204)

    def put(self, request, slug, *args, **kwargs):
        """
            PUT /api/v1/articles/<slug>/
        """
        permission_classes = (IsAuthenticated,)
        article = get_object_or_404(Article.objects.all(), slug=slug)
        if request.user.id != article.author_id:
            return Response({
                "message": error_msgs['article_owner_error']
            }, status=403)
        else:
            article_data = request.data
            article.updated_at = dt.datetime.utcnow()
            serializer = ArticleSerializer(
                instance=article,
                data=article_data,
                context={'request': request},
                partial=True
            )
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(
                    [
                        serializer.data,
                        [{"message": success_msg['article_update']}]
                    ], status=201
                )
            else:
                return Response(
                    serializer.errors,
                    status=400
                )


class TagAPIView(generics.ListAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, *args):
        """
            GET /api/v1/tags/
        """
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)

        if data:
            return Response({
                'message': success_msg['tag_get'],
                'tags': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'message': error_msgs['tags_not_found'],
        }, status=status.HTTP_404_NOT_FOUND)


def get_article(slug):
    """
        Returns specific article using slug
    """
    article = Article.objects.all().filter(slug=slug).first()
    if article is None:
        raise exceptions.NotFound({
            "message": error_msgs['not_found']
        }, status.HTTP_404_NOT_FOUND)
    return article


class ShareViaEmail(generics.CreateAPIView):
    """
        Share Articles via email
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        """
            POST a request to /api/v1/<slug>/share/email/
            share the article via email
        """
        email = request.data['email']
        get_article(slug)

        if not email:
            return Response({
                'message': error_msgs['no_email'],
            },
                status=status.HTTP_400_BAD_REQUEST)
        elif re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email) is None:
            return Response({
                'message': error_msgs['email_format']
            }, status=status.HTTP_400_BAD_REQUEST)

        username = request.user

        # format the email
        host = request.get_host()
        protocol = request.scheme
        shared_link = protocol + '://' + host + '/api/v1/articles/' + slug
        subject = "Authors Haven"
        article_title = get_article(slug)
        message = render_to_string(
            'article_share.html', {
                'username': str(username).capitalize(),
                'title': article_title,
                'link': shared_link
            })
        to_email = email
        from_email = os.getenv("DEFAULT_FROM_EMAIL")

        send_mail(
            subject,
            message,
            from_email, [
                to_email,
            ],
            html_message=message,
            fail_silently=False)

        message = {
            'message':
            success_msg['share_success'],
            'shared_link': shared_link
        }
        return Response(message, status=status.HTTP_200_OK)


class ShareViaFacebookAndTwitter(generics.CreateAPIView):
    """
        Share Articles via facebook or twitter
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        """
            Share Article depending on the POST request either
            /api/v1/<slug>/share/facebook/ or
            /api/v1/<slug>/share/twitter/
        """
        get_article(slug)
        host = request.get_host()
        protocol = request.scheme
        article_link = protocol + '://' + host + '/api/v1/articles/' + slug

        facebook_url = "https://www.facebook.com/sharer/sharer.php?u="
        twitter_url = "https://twitter.com/home?status="
        shared_link = None
        if request.path == '/api/v1/{}/share/facebook/'.format(slug):
            shared_link = facebook_url + article_link

        elif request.path == '/api/v1/{}/share/twitter/'.format(slug):
            shared_link = twitter_url + article_link

        message = {
            'message':
                success_msg['share_success'],
                'shared_link': shared_link
        }
        return Response(message, status=status.HTTP_200_OK)


class SearchView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer
    filter_class = ArticleFilter
    filter_backends = (SearchFilter, OrderingFilter,)
    search_fields = ('title', 'body',
                     'author__username', 'tags__tag')

    def get_queryset(self, request):
        """Overrides the get_queryset method"""

        queryset = Article.objects.all()
        author = self.request.query_params.get('author', None)
        title = self.request.query_params.get('title', None)
        body = self.request.query_params.get('body', None)
        tag = self.request.query_params.get('tag', None)

        if author:
            queryset = queryset.filter(author__username__icontains=author)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if body:
            queryset = queryset.filter(body__icontains=body)
        if tag:
            queryset = queryset.filter(tags__tag__icontains=tag)
        if queryset:
            return queryset
        else:
            raise exceptions.NotFound({
                "message": error_msgs['not_found']
            })

    def get(self, request):
        """
        Handles GET requests. Returns filtered results
        """

        serializer = self.serializer_class(
            self.get_queryset(request), context={
                'request': request
            }, many=True)
        results = serializer.data
        paginator = Paginator(results, 25)
        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
             # If page is not an integer, deliver first page.
            results = paginator.page(1)
        except EmptyPage:
             # If page is out of range (e.g. 9999), deliver last page of results.
            results = paginator.page(paginator.num_pages)
        return Response(results.object_list)
