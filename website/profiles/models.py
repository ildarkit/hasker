from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    icon = models.ImageField('avatar', blank=True)
    registration = models.DateTimeField('date registration', default=timezone.now)
