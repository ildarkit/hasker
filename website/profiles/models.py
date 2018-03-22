from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    icon = models.ImageField('avatar', upload_to='avatars/', blank=True)
    registration = models.DateTimeField('date registration', default=timezone.now)
