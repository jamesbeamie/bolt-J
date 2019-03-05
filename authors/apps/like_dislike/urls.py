from django.contrib import admin
from django.urls import path

from authors.apps.articles.models import Article
from authors.apps.comments.models import Comments

from . import views
from .models import LikeDislike

app_name = "like"

urlpatterns = [
    path('articles/<slug>/like/', views.PreferenceView.as_view(
        pref='Like', model=Article), name='article_like'),
    path('articles/<str:slug>/dislike/', views.PreferenceView.as_view(
        pref='Dislike', model=Article), name='article_dislike'),
    path('articles/<str:slug>/comments/<int:pk>/like/',
         views.PreferenceView.as_view(pref='Like', model=Comments),
         name='comment_like'),
    path('articles/<str:slug>/comments/<int:pk>/dislike/',
         views.PreferenceView.as_view(pref='Dislike', model=Comments),
         name='comment_dislike')
]
