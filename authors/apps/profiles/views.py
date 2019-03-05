from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import status
# local imports
from .models import Profile
from .serializers import UserProfileSerializer, UpdateUserProfileSerializer
from .renderers import ProfileJSONRenderer
from authors.apps.authentication.messages import error_msg, success_msg


class UserProfileView(RetrieveAPIView):
    """ 
    retrieves an authors profile information

    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=self.kwargs.get('username')
            )
            return profile
        except Exception:

            raise NotFound(error_msg['profile_not_there'])

    def retrieve(self, request, **kwargs):
        data = self.get_queryset()
        serializer = self.serializer_class(data, context={'request': request})

        return Response((serializer.data,
                         {"message": success_msg['profil_success']}),
                        status=status.HTTP_200_OK)


class AuthorsProfileListAPIView(ListAPIView):
    """
    Gets a list all authors profiles 
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = UserProfileSerializer

    # gets the whole list
    def get(self, request, *args, **kwargs):
        # here  we filter
        # we filter so that the user doesnot see his profile in the list
        data = Profile.objects.all().exclude(user=self.request.user)
        serializer = self.serializer_class(data, many=True)
        return Response((serializer.data,
                         {"message": success_msg['profil_success']}),
                        status=status.HTTP_200_OK)


class UpdateUserProfileView(UpdateAPIView):
    # here we update the users profile
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = UpdateUserProfileSerializer
    queryset = Profile.objects.all()

    # we make a query
    # the check  who wants to make an update
    # we check if they own the account
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.select_related('user').get(
            user__username=self.request.user.username
        )
        return obj

    # we use the patch method to ensure we only update what we want and not the entire object
    def patch(self, request, username):
        if request.user.username != username:
            raise PermissionDenied(error_msg['cannot_update_profile'])
        else:
            data = request.data
            serializer = self.serializer_class(instance=request.user.profiles,
                                               data=data, partial=True)
            serializer.is_valid()
            serializer.save()
            return Response((serializer.data,
                             {"message": success_msg['profil_update']}),
                            status=status.HTTP_200_OK)

class FollowingView(CreateAPIView):
    """
    This class enables users to follow and unfollow eachother
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def post(self, request, *args, **kwargs):
        """
        Follows a user
        """
        username = kwargs.get('username')
        profile = Profile.objects.get(user__username=username)
        current_profile = request.user.profiles
        
        #checks if the authenticated user follows the current user
        if current_profile.user.username == profile.user.username:
            return Response({"message":error_msg['cannot_followself']}, 
                            status=status.HTTP_400_BAD_REQUEST)

        current_profile.toggle_follow(profile.user)
        serializer = self.serializer_class(profile, context={
            'request': request})

        if (serializer.data['following']):
            message = success_msg['success_followed']
        else:
            message = success_msg['success_unfollowed']

        return Response((serializer.data, 
                        {"message": message}), 
                            status=status.HTTP_201_CREATED)


class FollowList(ListAPIView):
    """
    This class returns the user follow list of the current user
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def list(self, request, *args, **kwargs):
        username = kwargs.get('username')
        profile = Profile.objects.get(user__username=username)
        queryset = profile.get_following()
        serializer = self.serializer_class(queryset, many=True,
                                           context={'request': request})
        return Response((serializer.data,
                        {"message": success_msg['user_following']}),
                            status=status.HTTP_200_OK)

class FollowerList(ListAPIView):
    """
    This class returns the user follower list of the current user
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)
    queryset = Profile.objects.all()

    def list(self, request, *args, **kwargs):
        username = kwargs.get('username')
        profile = Profile.objects.get(user__username=username)
        queryset = profile.user.followers
        serializer = self.serializer_class(queryset, many=True,
                                           context={'request': request})
        return Response((serializer.data, 
                        {"message": success_msg['user_followers']}),
                        status=status.HTTP_200_OK)