from django.db import models
from django.contrib.auth.models import User


class HaskerUser(User):
    icon = models.ImageField()
    registration = models.DateTimeField('date registration')


class Question(models.Model):
    header = models.CharField(max_length=255)
    author = models.ForeignKey(HaskerUser, on_delete=models.CASCADE)
    question_text = models.TextField()
    pub_date = models.DateTimeField('date published')


class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(HaskerUser, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')
    is_correct = models.BooleanField()
    votes = models.IntegerField(default=0)


class Tag(models.Model):
    tag = models.SlugField(unique=True)