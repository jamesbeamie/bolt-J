"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1.4/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Authors' Haven API",
        default_version='v1',
        description="Authors' Haven",
        license=openapi.License(name="MIT Licence"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# urls
urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/v1/', include('authors.apps.like_dislike.urls',
                            namespace='likes')),
    path('swagger.json',
         schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml',
         schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
    path('swagger/', schema_view.with_ui(
        'swagger',
        cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/', include('authors.apps.authentication.urls'), name='apiv1'),
    path('api/v1/', include('authors.apps.profiles.urls',
                            namespace='profile'), name='apiv1'),
    path('api/v1/', include('authors.apps.articles.urls')),
    path('api/v1/', include('authors.apps.rating.urls')),
    path('api/v1/', include('authors.apps.comments.urls')),
    path('api/v1/', include('authors.apps.reading_stats.urls')),
    path('api/v1/', include("authors.apps.favorite.urls")),
]
