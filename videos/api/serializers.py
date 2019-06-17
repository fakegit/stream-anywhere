from pathlib import Path

import magic
from django.conf import settings
from rest_framework import serializers
from rest_framework.reverse import reverse
from videos.models import Collection, Video


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        depth = 1
        fields = (
            'id', 'name', 'path', 'status', 'created_at', 'updated_at', 'recursive',
        )
        read_only_fields = ()


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        depth = 1
        fields = (
            'id', 'name', 'path', 'status', 'created_at', 'updated_at', 'checksum', 'position', 'duration',
            'collection', 'started_at', 'finished_at', 'played_at',
        )
        read_only_fields = ()


class PathSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    mimetype = serializers.SerializerMethodField()

    def get_url(self, obj: Path):
        path = str(obj.absolute()).replace(settings.ROOT_PATH, '', 1)
        url = reverse('path-detail', kwargs=dict(pk=path))
        if obj.is_dir():
            url += '/'
        return self.context['request'].build_absolute_uri(url)

    def get_type(self, obj: Path):
        if obj.is_dir():
            return 'directory'
        elif obj.is_file():
            return 'file'
        elif obj.is_socket():
            return 'socket'
        elif obj.is_symlink():
            return 'symlink'
        elif obj.is_block_device():
            return 'block_device'
        elif obj.is_reserved():
            return 'reserved'
        elif obj.is_char_device():
            return 'char_device'
        elif obj.is_fifo():
            return 'fifo'
        else:
            return 'unknown'

    def get_mimetype(self, obj: Path):
        if obj.is_dir():
            return 'inode/directory'
        elif obj.is_file():
            return magic.from_file(str(obj.absolute()), mime=True)

#
#
# class DirectorySerializer(serializers.Serializer):
#     name = serializers.CharField()
#
#     children = PathSerializer(many=True, source='get_children')
#
#     def get_children(self):
#         yield
#