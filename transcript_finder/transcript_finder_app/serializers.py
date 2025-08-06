from rest_framework import serializers
from transcript_finder_app.models import Channel, Video, Transcript

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"

class ChannelSerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Channel
        fields = ['id', 'name', 'video_count']

class ChannelVideosSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Channel
        fields = "__all__"