import json

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.views import View

from authors.apps.articles.models import Article
from authors.apps.authentication.utils import status_codes, swagger_body
from authors.apps.comments.models import Comments
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework import exceptions, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .messages import statusmessage, success
from .models import LikeDislike
from .renderers import LikeDislikeJSONRenderer
from .serializers import PreferenceSerializer


class PreferenceView(generics.GenericAPIView):
    """Preference view"""

    permission_classes = (IsAuthenticated,)
    renderer_classes = (LikeDislikeJSONRenderer,)
    serializer_class = PreferenceSerializer
    pref = None  # Preference type Like/Dislike
    model = None  # Model (Articles/Comments)
    swagger_schema = SwaggerAutoSchema

    @swagger_auto_schema(
        request_body=swagger_body(None),
        responses=status_codes(codes=(200, 401))
    )
    def post(self, request, slug=None, pk=None):
        """
        Handles requests to like or dislike articles and comments
        """
        item = None
        queryset = self.model.objects.all()
        options = {
            'Like': 1,
            'Dislike': -1
        }
        pref_status = options[self.pref]
        if self.model is Article:
            item = queryset.get(slug=slug)
        elif self.model is Comments:
            item = queryset.get(pk=pk)
        try:
            obj = LikeDislike.objects.get(
                content_type=ContentType.objects.get_for_model(item),
                object_id=item.id,
                user=request.user)
            if int(obj.pref) != pref_status:
                obj.pref = pref_status
                obj.save(update_fields=['pref'])
                result, like_status = success.get(
                    self.pref), statusmessage.get(self.pref)
            else:
                obj.delete()
                result, like_status = success.get(
                    'Null'), statusmessage.get('Null')
        except LikeDislike.DoesNotExist:
            item.prefs.create(
                user=request.user, pref=pref_status)
            result, like_status = success.get(
                self.pref), statusmessage.get(self.pref)
        return Response({
            "result": result,
            "status": like_status,
            "like_count": item.prefs.count('likes'),
            "dislike_count": item.prefs.count('dislikes')
        }, status=status.HTTP_201_CREATED
        )
