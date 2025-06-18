from django.db import models


class Channel(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Video(models.Model):
    url = models.CharField(max_length=100)
    title = models.CharField(max_length=100)

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='videos'
    )

class Transcript(models.Model):
    transcript = models.TextField()

    video = models.OneToOneField(
        Video,
        on_delete=models.CASCADE,
        related_name='transcript'
    )

    
    