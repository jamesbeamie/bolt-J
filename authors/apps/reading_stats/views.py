from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ReadStatsSerializers
from .models import ReadStats
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from authors.apps.authentication.messages import read_stats_message


class UserReadStatsView(ListAPIView):
    serializer_class = ReadStatsSerializers

    def get_queryset(self):
        """"
            This gets all the articles the user has read
        """
        return ReadStats.objects.filter(user=self.request.user)


class UserCompleteStatView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, slug):
        """
           This method checks if the articlle an user is accesing is available
           article__slug specidies that the slug is from the articles object
           if a no article with such slug exists then it throws an error
        """
        try:
            user_stat = ReadStats.objects.get(article__slug=slug)
        except ReadStats.DoesNotExist:
            return Response({
                "message": read_stats_message['read_error']},
                status=status.HTTP_404_NOT_FOUND)
        if user_stat.article_read:
            return Response({
                "message": read_stats_message['read_update']
            }, status=status.HTTP_403_FORBIDDEN)

        user_stat.article_read = True
        user_stat.save()

        return Response(
            {
                "message": read_stats_message['read_status']
            }, status.HTTP_200_OK
        )
