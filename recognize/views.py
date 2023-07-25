from django.shortcuts import render

# Create your views here.
from recognize.models import Profile, KnownImage

from rest_framework import generics

from .serializers import (
    ProfileOnlySerializer, 
    KnownImageOnlySerializer, 
    NestedKnownImageSerializer, 
    NestedProfileSerializer, 
    CheckFaceSerializer
    )

from rest_framework.permissions import AllowAny, IsAuthenticated
import string
from rest_framework.pagination import LimitOffsetPagination

from rest_framework.response import Response
####################################
# ListCreate:
####################################


class ProfileListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        return Profile.objects.all()
    def get_serializer_class(self):
        if self.request.method.upper() == "GET":
            return NestedProfileSerializer
        else:
            return ProfileOnlySerializer
    permission_classes = [
        AllowAny,
    ]
    ordering_fields = '__all__'
    filterset_fields = '__all__'
    
    pagination_class = LimitOffsetPagination

    def paginate_queryset(self, queryset):
        print(self.paginator)
        if self.paginator and self.request.query_params.get(self.paginator.limit_query_param, None) is None:
            return None
        return super().paginate_queryset(queryset)


class KnownImageListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        return KnownImage.objects.all()
    def get_serializer_class(self):
        if self.request.method.upper() == "GET":
            return NestedKnownImageSerializer
        else:
            return KnownImageOnlySerializer
    permission_classes = [
        AllowAny,
    ]
    ordering_fields = '__all__'
    filterset_fields = '__all__'
    
    pagination_class = LimitOffsetPagination

    def paginate_queryset(self, queryset):
        print(self.paginator)
        if self.paginator and self.request.query_params.get(self.paginator.limit_query_param, None) is None:
            return None
        return super().paginate_queryset(queryset)

####################################
# Edits:
####################################


class ProfileEditsView(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Profile.objects.all()
    lookup_field = 'id'
    def get_serializer_class(self):
        if self.request.method.upper() == "GET":
            return NestedProfileSerializer
        else:
            return ProfileOnlySerializer
    permission_classes = [
        AllowAny,
    ]


class KnownImageEditsView(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return KnownImage.objects.all()
    lookup_field = 'id'
    def get_serializer_class(self):
        if self.request.method.upper() == "GET":
            return NestedKnownImageSerializer
        else:
            return KnownImageOnlySerializer
    permission_classes = [
        AllowAny,
    ]


####################################
# CheckFace:
####################################


class CheckFaceView(generics.GenericAPIView):
    def get_queryset(self):
        return Profile.objects.filter(matching_id=self.request.data['matching_id'])
    
    def get_serializer_class(self):
        return super().get_serializer_class()
    
    serializer_class = CheckFaceSerializer
    
    def post(self, request, *args, **kwargs):
        matching_id = self.request.data['matching_id']
        image_url = self.request.data['image']
        response = {
            "matching_id": matching_id,
            "image": image_url,
            "is_matched": None,
            "result": None
        }
        from recognize.recognize import FaceRecognize
        fr = FaceRecognize()
        result = fr.match_faces_from_url(url=image_url, matching_id=matching_id)
        response['result'] = result
        response['is_matched'] = result['is_matched']
        return Response(response)