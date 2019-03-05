from django.urls import path
from .views import CreateCommentAPiView, CommentApiView

app_name = 'comments'
urlpatterns = [
    path('articles/<slug>/comments/',
         CreateCommentAPiView.as_view(),
         name='comment'),
    path('articles/<slug>/comments/<int:id>/',
         CommentApiView.as_view(),
         name='specific_comment'),
]
