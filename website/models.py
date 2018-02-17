from django.db import models
from django.contrib.auth.models import User


class HaskerUser(User):
    icon = models.ImageField()
    registration = models.DateTimeField('date registration')


class BaseModel(HaskerUser):
    author = models.ForeignKey(HaskerUser, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        abstract = True


class Question(BaseModel):
    header = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')


class Answer(BaseModel):
    pub_date = models.DateTimeField('date published')
    is_correct = models.BooleanField()
    votes = models.IntegerField(default=0)


class Tag(models.Model):
    tag = models.SlugField(unique=True)