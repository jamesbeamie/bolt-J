from django.urls import path

from .views import (ArticleAPIView, SearchView, ShareViaEmail,
                    ShareViaFacebookAndTwitter, SpecificArticle, TagAPIView)

app_name = "articles"

urlpatterns = [
    path('articles/', ArticleAPIView.as_view(), name="articles"),
    path('tags/', TagAPIView.as_view(), name="tags"),
    path('articles', SearchView.as_view(), name="search-articles"),
    path('articles/<str:slug>/', SpecificArticle.as_view(),
         name="specific_article"),
    path('tags/', TagAPIView.as_view(), name="tags"),
    path('articles/<str:slug>/',
         SpecificArticle.as_view(), name="specific_article"),
    path('<slug>/share/email/',
         ShareViaEmail.as_view(), name='email_share'
         ),
    path('<slug>/share/facebook/',
         ShareViaFacebookAndTwitter.as_view(), name='facebook_share'
         ),
    path('<slug>/share/twitter/',
         ShareViaFacebookAndTwitter.as_view(), name='twitter_share'
         )
]
