from django.db import models

class User(models.Model):
    login = models.CharField(max_length=20)
    password = models.CharField()
    email = models.EmailField()
    icon = models.CharField()
    registration = models.DateTimeField('date registration')

class Question(models.Model):
    header = models.CharField(max_length=50)
    autor = models.ManyToOneRel()
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

class Answer(models.Model):
    text = models.CharField(max_length=200)
    autor = models.ManyToOneRel()
    pub_date = models.DateTimeField('date published')
    correct = models.BooleanField()
    votes = models.IntegerField(default=0)

class Tag(models.Model):
    tag = models.SlugField(unique=True)