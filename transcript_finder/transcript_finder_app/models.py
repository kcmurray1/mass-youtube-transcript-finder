from django.db import models


class Channel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"

class Video(models.Model):
    url = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100)
    date = models.DateField(null=True)
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='videos'
    )

    def __str__(self):
        return f"{self.title} uploaded {self.date} by the channel {self.channel}"

class Transcript(models.Model):
    transcript = models.TextField()

    video = models.OneToOneField(
        Video,
        on_delete=models.CASCADE,
        related_name='transcript'
    )

    