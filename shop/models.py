import uuid
from django.db import models
from django.conf import settings

class Music(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    file = models.FileField(upload_to='music/')
    price = models.PositiveIntegerField(default=10) # 도토리 가격

    def __str__(self):
        return f"{self.title} - {self.artist}"

class UserMusic(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchased_musics')
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'music')

class UserOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
