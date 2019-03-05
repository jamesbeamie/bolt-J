from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import status

from .models import Profile


class UserProfileSerializer(serializers.ModelSerializer):
    """ 
     Here we serialize the data 
     helps convert queryset into datatypes so that we can render them as json

    """
    # Returns the username
    username = serializers.CharField(source='user.username', read_only=True)
    image = serializers.ImageField(default=None)
    following = serializers.SerializerMethodField()

    def get_following(self, instance):
        request = self.context.get('request', None)
        
        if request is None:
            return None

        user_to_check = request.user.profiles
        status = user_to_check.if_following(instance)
        return status

    class Meta:
        model = Profile

        fields = ('username', 'image', 'bio', 'location', 'First_name',
                  'Last_name', 'following',
                  'company', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'username')

class UpdateUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile

        fields = ('image', 'bio', 'location', 'company', 'First_name',
                  'Last_name')
        read_only_fields = ('created_at', 'updated_at')

        def update(self, instance, validated_data):

            instance.bio = validated_data.get('bio', instance.bio)
            instance.image = validated_data.get('image', instance.image)
            instance.company = validated_data.get('company', instance.company)
            instance.First_name = validated_data.get('First_name',
                                                     instance.First_name)
            instance.Last_name = validated_data.get('Last_name',
                                                    instance.Last_name)
            instance.location = validated_data.get(
                'location', instance.location)

            instance.save()
            return instance
