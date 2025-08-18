from django.urls import path
from transcript_finder_app.views import ChannelCollection, ChannelRecord, TranscriptSearchAPI

urlpatterns = [
    path("channels", ChannelCollection.as_view(), name='channel-collection'),
    path("channel/<int:pk>", ChannelRecord.as_view(), name='channel-record'),
    path("channel/search", TranscriptSearchAPI.as_view(), name='channel-search')

]