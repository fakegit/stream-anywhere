import os
from pathlib import Path
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from videos.models import Collection, Video
from videos.api.serializers import CollectionSerializer, VideoSerializer, PathSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    search_fields = (
        'name', 'path', 'status',
    )
    filter_fields = (
        'id', 'name', 'path', 'status', 'created_at', 'updated_at',
    )
    ordering_fields = (
        'id', 'name', 'path', 'status', 'created_at', 'updated_at', 'recursive',
    )


class VideoViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    search_fields = (
        'name', 'path', 'status', 'checksum',
    )
    filter_fields = (
        'id', 'name', 'path', 'status', 'created_at', 'updated_at', 'checksum', 'position', 'duration',
        'started_at', 'finished_at', 'played_at',
    )
    ordering_fields = (
        'id', 'name', 'path', 'status', 'created_at', 'updated_at', 'checksum', 'position', 'duration',
        'collection', 'started_at', 'finished_at', 'played_at',
    )

    def perform_create(self, serializer):
        user: Union[AbstractUser, None] = self.request.user
        user = user if user.is_authenticated else None
        user = user or get_user_model().objects.get(username='default')
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED if serializer.created else status.HTTP_200_OK,
                        headers=headers)


class PathViewSet(viewsets.GenericViewSet):
    serializer_class = PathSerializer
    lookup_value_regex = '.*'

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        path = os.path.join(settings.ROOT_PATH, self.kwargs.get(lookup_url_kwarg, ''))
        return Path(path)

    def get_queryset(self):
        return self.get_object().iterdir()

    def filter_queryset(self, queryset):
        return filter(lambda x: not x.name.startswith('.'), queryset)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_dir():
            serializer = self.get_serializer(self.filter_queryset(instance.iterdir()), many=True)
        else:
            serializer = self.get_serializer(instance)
        return Response(serializer.data)

