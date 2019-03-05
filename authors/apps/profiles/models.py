from django.db import models
from django.db.models.signals import post_save
from cloudinary.models import CloudinaryField

# local import
from ..authentication.models import User


class Profile(models.Model):
    """

    Here create the profiles models, we decaler the fields we want included

    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profiles')
    is_following = models.ManyToManyField(
        User, related_name='followers', symmetrical=False)
    bio = models.TextField(blank=True)
    image = CloudinaryField(
        "image",
        default='https://res.cloudinary.com/dxecwuaqd/image/upload/v1550079584/o75xgubltk4hso90l9jt.png')
    First_name = models.CharField(max_length=50, blank=True)
    Last_name = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # returns string representation of object

    def __str__(self):
        return str(self.user.username)
    # follows a user

    def follow(self, profile):
        self.is_following.add(profile)

    # unfollows a user
    def unfollow(self, profile):
        self.is_following.remove(profile)

    def toggle_follow(self, profile):
        if self.if_following(profile):
            return self.unfollow(profile)
        return self.follow(profile)

    # append the profile user list to get the user followers

    def get_following(self, profile=None):
        users = self.is_following.all()
        profile_list = [item.profiles for item in users]
        return profile_list

    # checks if the user profile is in the is_following list
    def if_following(self, profile):
        return self.is_following.filter(pk=profile.pk).exists()


def create_profile(sender, instance, created, **kwargs):
    # this creates a user profile when a user object is created
    if created:
        instance.profile = Profile.objects.create(user=instance)


# this saves the user profile created
post_save.connect(create_profile, sender=User)
