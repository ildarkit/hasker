from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .validators import validate_max_list_length, validate_comma_separated_tags_list

from website.profiles.models import Profile


class Question(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='questions',
                               on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    text = models.TextField()
    tags = models.CharField(validators=[validate_max_list_length,
                                        validate_comma_separated_tags_list], max_length=255)
    up_votes = models.ManyToManyField(get_user_model(), related_name='up_question_votes')
    down_votes = models.ManyToManyField(get_user_model(), related_name='down_question_votes')
    rating = models.IntegerField(default=0)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.header.lower().replace(' ', '-')

    def tags_as_list(self):
        return self.tags.split(', ')

    def add_question_tags(self):
        """ Добавление тэгов к вопросу"""
        related_tags = []
        for tag_name in self.tags.split(','):
            tag_name = tag_name.strip()
            try:
                tag = Tag.objects.get(name=tag_name)
            except ObjectDoesNotExist:
                tag = Tag.objects.create(name=tag_name)
            related_tags.append(tag)
        self.related_tags.add(*related_tags)

    def set_author(self, request):
        """ Добавление автора вопроса"""
        request.session['new_question_id'] = self.pk
        self.author = Profile.objects.get(pk=request.user.pk)
        self.save()


class Tag(models.Model):
    name = models.SlugField(unique=True)
    question = models.ManyToManyField(Question, related_name='related_tags')


class Answer(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='answers',
                               on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers',
                                 on_delete=models.CASCADE)
    answer_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=timezone.now)
    is_correct = models.BooleanField(default=False)
    up_votes = models.ManyToManyField(get_user_model(), related_name='up_answer_votes')
    down_votes = models.ManyToManyField(get_user_model(), related_name='down_answer_votes')
    rating = models.IntegerField(default=0)

    #def send_email(self):
    #    self.email

    class Meta:
        ordering = ["-rating", "-pub_date"]

    def set_author(self, request):
        self.author = Profile.objects.get(pk=request.user.pk)
        self.save()
