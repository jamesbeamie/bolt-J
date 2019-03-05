from django.urls import path

from .views import UserReadStatsView, UserCompleteStatView 



app_name = "read"

urlpatterns = [
    path("read-stats/", UserReadStatsView.as_view(), name="user_read_stats"),
    path("read/<str:slug>/", UserCompleteStatView.as_view(), name="article_read"),
]