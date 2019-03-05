from django.urls import path

from .views import (UserProfileView, AuthorsProfileListAPIView,
                    UpdateUserProfileView, FollowingView, FollowList, FollowerList)


app_name = "prof"

urlpatterns = [
    path('profiles/', AuthorsProfileListAPIView.as_view(),
         name='authors_profile'),
    path('profiles/<str:username>/', UserProfileView.as_view(),
         name='profile'),
    path('profiles/<str:username>/edit/', UpdateUserProfileView.as_view(), 
         name='update_profile'),
    path('profiles/<username>/follow', FollowingView.as_view(), 
         name='follow'),
    path('profiles/<username>/followers', FollowerList.as_view(), 
         name='followers'),
    path('profiles/<username>/following', FollowList.as_view(), 
         name='following'),
]
