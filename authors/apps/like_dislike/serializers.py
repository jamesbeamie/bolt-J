import re
from rest_framework import serializers
from .models import LikeDislike


class PreferenceSerializer(serializers.ModelSerializer):
    """Serializers"""

    class Meta:
        model = LikeDislike
        fields = '__all__'
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
