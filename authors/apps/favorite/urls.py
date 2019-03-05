from django.urls import path

from authors.apps.favorite.views import FavoriteAPIView, UnfavoriteAPIView, GetOwnFavoritesAPIView

app_name = "fav"

urlpatterns = [
    path('articles/<slug>/favorite/',
         FavoriteAPIView.as_view(), name="favorite-article"),
    path('articles/<slug>/unfavorite/',
         UnfavoriteAPIView.as_view(), name="unfavorite-article"),
    path('favorites/', GetOwnFavoritesAPIView.as_view(), name="favorites")
]
