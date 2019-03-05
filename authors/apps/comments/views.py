from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .serializers import CommentSerializer
from .utils import Utils
from .models import Comments
from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from ..authentication.messages import error_msg, success_msg


class CreateCommentAPiView(generics.ListCreateAPIView):
    """
        View class to create and fetch comments
    """
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = CommentSerializer

    queryset = Comments.objects.all()
    util = Utils()

    def post(self, request, *args, **kwargs):
        '''This method creates a comment on an article'''
        slug = self.kwargs['slug']
        article = self.util.check_article(slug)
        comment = request.data['comment']
        serializer = self.serializer_class(data=comment, context={
            'request': request
        })
        author_profile = Profile.objects.get(user=request.user)
        serializer.is_valid()
        serializer.save(author_profile=author_profile,
                        article_id=article.id,
                        )
        result = {"message": success_msg["added_comment"]}
        result.update(serializer.data)
        return Response(result,
                        status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        '''This method gets all comments for an article'''
        slug = self.kwargs['slug']
        article = self.util.check_article(slug)
        comments = self.queryset.filter(article_id=article.id)
        serializer = self.serializer_class(comments, context={'request':request}, many=True)
        return Response({"comments": serializer.data,
                         "commentsCount": comments.count()
                         }, status=status.HTTP_200_OK)



                         


class CommentApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    util = Utils()
    queryset = Comments.objects.all()

    def get(self, request, id, *args, **kwargs):
        '''This method gets a single comment by id'''

        slug = self.kwargs['slug']
        article = self.util.check_article(slug)
        comment = self.util.check_comment(id)
        serializer = self.serializer_class(comment, context={
            'request': request
        })
        return Response({"comment": serializer.data})

    def delete(self, request, id, *args, **kwargs):
        '''This method deletes a comment'''

        slug = self.kwargs['slug']
        article = self.util.check_article(slug)
        comment = self.util.check_comment(id)

        if request.user.pk == comment.author_profile.id:
            self.perform_destroy(comment)
            msg = success_msg["deleted_comment"]
            return Response({
                "message": msg
            }, status=status.HTTP_200_OK)
        else:
            msg = error_msg["restricted"]
            return Response({
                "message": msg
            }, status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, id, *args, **kwargs):
        '''This method updates a comment'''

        slug = self.kwargs['slug']
        article = self.util.check_article(slug)
        comment = self.util.check_comment(id)
        if request.user.pk == comment.author_profile.id:
            existing_field = request.data.copy()
            comment.body = existing_field['comment']['body']

            serializer = CommentSerializer(
                instance=comment, data=existing_field['comment'], context={
                    'request': request
                })
            if serializer.is_valid():
                serializer.save(author_profile=comment.author_profile)
                msg = success_msg["update_success"]
                return Response({
                    "message": msg
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            msg = {"error": error_msg["Unauthorized"]}
            return Response({
                "message": msg
            }, status=status.HTTP_401_UNAUTHORIZED)
