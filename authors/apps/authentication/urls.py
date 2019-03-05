from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    VerifyAPIView, PasswordResetRequestAPIView, ResetPasswordAPIView,
    SocialSignInSignOut
)

app_name = "auth"

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='user'),
    path('users/', RegistrationAPIView.as_view(), name="register"),
    path('users/login/', LoginAPIView.as_view(), name="login"),
    path('users/verify/<token>', VerifyAPIView.as_view(), name='email-verify'),
    path('users/password_request/', PasswordResetRequestAPIView.as_view(),
         name="reset_request"),
    path('users/password_reset/<str:token>',
         ResetPasswordAPIView.as_view(), name="password_reset"),
    path('social_auth/', SocialSignInSignOut.as_view(),
         name="social_signin_signup"),
]
