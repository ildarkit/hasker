from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from .validators import validate_max_list_length, validate_comma_separated_tags_list


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    icon = models.ImageField('avatar', blank=True)
    registration = models.DateTimeField('date registration', default=timezone.now)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Question(models.Model):
    author = models.ForeignKey(Profile, related_name='questions',
                               on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    text = models.TextField()
    tags = models.CharField(validators=[validate_max_list_length,
                                        validate_comma_separated_tags_list], max_length=255)
    up_votes = models.ManyToManyField(User, related_name='up_question_votes')
    down_votes = models.ManyToManyField(User, related_name='down_question_votes')
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.header.lower().replace(' ', '-')

    def tags_as_list(self):
        return self.tags.split(', ')


class Tag(models.Model):
    name = models.SlugField(unique=True)
    question = models.ManyToManyField(Question, related_name='related_tags')


class Answer(models.Model):
    author = models.ForeignKey(Profile, related_name='answers',
                               on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers',
                                 on_delete=models.CASCADE)
    answer_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=timezone.now)
    is_correct = models.BooleanField(default=False)
    up_votes = models.ManyToManyField(User, related_name='up_answer_votes')
    down_votes = models.ManyToManyField(User, related_name='down_answer_votes')
    rating = models.IntegerField(default=0)

    #def send_email(self):
    #    self.email

    class Meta:
        ordering = ["rating", "-pub_date"]
