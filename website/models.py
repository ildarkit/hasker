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

    def __str__(self):
        return self.header.replace(' ', '-')


class Tag(models.Model):
    tag = models.SlugField(unique=True)
    question = models.ManyToManyField(Question)


class Answer(models.Model):
    author = models.ForeignKey(HaskerUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')
    is_correct = models.BooleanField(default=False)
    votes = models.PositiveIntegerField(default=0)
    text = models.TextField()

    #def send_email(self):
    #    self.email

    class Meta:
        ordering = ["-pub_date"]
