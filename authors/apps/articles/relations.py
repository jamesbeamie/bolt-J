import re
from rest_framework import serializers
from authors.apps.articles.models import Tags
from .messages import error_msgs
from rest_framework.exceptions import ValidationError


class TagsRelation(serializers.RelatedField):
    """This class overwrites the serializer class for tags
    to enable tags to be saved on a separate table when
    creating an article
    """

    def get_queryset(self):
        """
            Gets all tags from the tag model
        """
        return Tags.objects.all()

    def to_representation(self, value):
        """
            Converts the initial datatype into serializable datatype.
        """
        return value.tag

    def to_internal_value(self, data):
        """
            Restores the datatype into its internal python representation.
            This method should raise a serializers.ValidationError
            if the data is invalid
        """
        if len(data) == 0:
            tag, created = Tags.objects.get_or_create(tag=data)
            return tag

        if not re.match(r'^[a-zA-Z0-9][ A-Za-z0-9_-]*$', data):
            raise ValidationError(
                detail={'message': error_msgs['invalid_tag']})

        capitalized_tag = str(data).title()
        tag, created = Tags.objects.get_or_create(tag=capitalized_tag)
        return tag
