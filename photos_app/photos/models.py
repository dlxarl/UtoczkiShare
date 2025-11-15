from django.db import models
from django.contrib.auth.models import User

class Photo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    file = models.ImageField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'photos'

class PhotoShare(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='shares')
    shared_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_photos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'photos'
        unique_together = ('photo', 'shared_to')
