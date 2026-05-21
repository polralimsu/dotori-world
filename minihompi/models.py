from django.db import models
from django.conf import settings

class IlchonPyeong(models.Model):
    hompi_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ilchonpyeongs', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='authored_ilchonpyeongs', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
