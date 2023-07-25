"""face_recognition URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from recognize.views import (
    ProfileListCreateView,
    KnownImageListCreateView,
    ProfileEditsView,
    KnownImageEditsView,
    CheckFaceView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="FaceRecognition API Service",
        default_version='v1',
        description="",
        contact=openapi.Contact(email="parsadany@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('recognize/profile/list_create/', ProfileListCreateView.as_view(), name="ProfileListCreateView"),
    path('recognize/known_image/list_create/', KnownImageListCreateView.as_view(), name="KnownImageListCreateView"),
    path('recognize/profile/edits/<id>/', ProfileEditsView.as_view(), name="ProfileEditsView"),
    path('recognize/known_image/edits/<id>/', KnownImageEditsView.as_view(), name="KnownImageEditsView"),
    path('recognize/check_face/', CheckFaceView.as_view(), name="CheckFaceView"),


    path('api-auth/', include('rest_framework.urls')),
    path('redoc/', schema_view.with_ui('redoc',
                                       cache_timeout=0), name='schema-redoc'),
    path('swagger/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('postman/', schema_view.without_ui(cache_timeout=0),
         name='schema-swagger-postman'),
]
