from django.db import models
from django.contrib.auth.models import User


class HaskerUser(User):
    icon = models.ImageField()
    registration = models.DateTimeField('date registration')


class Question(models.Model):
    author = models.ForeignKey(HaskerUser, on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')
    text = models.TextField()


class Answer(models.Model):
    author = models.ForeignKey(HaskerUser, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')
    is_correct = models.BooleanField()
    votes = models.IntegerField(default=0)
    text = models.TextField()

    class Meta:
        ordering = ["-pub_date"]


class Tag(models.Model):
    tag = models.SlugField(unique=True)