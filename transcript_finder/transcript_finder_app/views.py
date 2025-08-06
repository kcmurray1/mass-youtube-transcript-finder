from rest_framework import generics
from transcript_finder_app.models import Video, Channel, Transcript
from transcript_finder_app.serializers import ChannelSerializer, ChannelVideosSerializer
from django.db.models import Count


class ChannelCollection(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.query_params.get('include_videos') == 'true':
            return ChannelVideosSerializer
        return ChannelSerializer

    def get_queryset(self):
        queryset = Channel.objects.annotate(video_count=Count('videos'))
        return queryset

class ChannelRecord(generics.RetrieveUpdateDestroyAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

