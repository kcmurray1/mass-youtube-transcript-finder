from rest_framework import serializers
from transcript_finder_app.models import Channel, Video, Transcript

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'