import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    main_video = models.FileField(upload_to='videos/', null=True, blank=True)
    profile_text = models.TextField(blank=True)
    dotori_balance = models.PositiveIntegerField(default=0)
    bgm = models.ForeignKey('shop.Music', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Friendship(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
