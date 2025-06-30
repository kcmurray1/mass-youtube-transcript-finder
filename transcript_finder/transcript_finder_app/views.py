from rest_framework import generics
from transcript_finder_app.models import Video, Channel, Transcript
from transcript_finder_app.serializers import ChannelSerializer

class ChannelCollection(generics.ListCreateAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

class ChannelRecord(generics.RetrieveUpdateDestroyAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

