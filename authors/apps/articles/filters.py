from django_filters import rest_framework as filter
from .models import Article


class ArticleFilter(filter.FilterSet):

    title = filter.CharFilter(
        field_name='title',
        lookup_expr='icontains'
    )
    body = filter.CharFilter(
        field_name='body',
        lookup_expr='icontains'
    )

    author = filter.CharFilter(
        field_name='author__username',
        lookup_expr='icontains'
    )

    tags = filter.CharFilter(
        field_name='tags__tag',
        lookup_expr='icontains'
    )

    class Meta:
        model = Article
        fields = ('title', 'body', 'author', 'tags')
