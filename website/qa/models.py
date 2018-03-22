from django.db.models import Q
from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .validators import validate_max_list_length, validate_comma_separated_tags_list


class Entity(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', default=timezone.now)
    rating = models.IntegerField(default=0)

    @transaction.atomic
    def vote(self, user, vote_type):
        v = Votes.objects.filter(Q(question=self.pk) | Q(answer=self.pk), user=user)
        if v.exists():
            self.rating -= v[0].vote_type
            v.delete()
        else:
            if isinstance(self, Question):
                Votes.objects.create(user=user, question=self, vote_type=vote_type)
            elif isinstance(self, Answer):
                Votes.objects.create(user=user, answer=self, vote_type=vote_type)
            self.rating += vote_type
        self.save()

    class Meta:
        abstract = True


class Question(Entity):
    author = models.ForeignKey(get_user_model(), related_name='questions',
                               on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    slug = models.SlugField(max_length=265, unique=True)
    tags = models.CharField(validators=[validate_max_list_length,
                                        validate_comma_separated_tags_list], max_length=255)

    class Meta:
        ordering = ["-rating", "-pub_date"]

    def __str__(self):
        return self.slug

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

    def set_author(self, user):
        """ Добавление автора вопроса"""
        self.author = user
        self.save()

    def get_time_delta(self):
        delta = timezone.now() - self.pub_date
        return ' {} days ago'.format(delta.days) if delta.days else ' {} hour ago'.format(delta.seconds // 3600)

    def short_header(self):
        return self.header[:18] + '...' if len(self.header) >= 18 else self.header

    def _get_slug(self):
        slug = slugify(self.header)
        n = 1
        result = slug
        while Question.objects.filter(slug=result).exists():
            result = '{}-{}'.format(slug, n)
        return result

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_slug()
        super().save()

    def notify_user(self, user, answer, link):
        send_mail('You have a new answer on the Hasker',
                  'The answer is:\n' + answer.text + '\n\n' +
                  'Here is the link for your question ' + link,
                  'from@example.com', [user.email],
                  fail_silently=False)

    def set_correct_answer(self, answer):
        # Автор вопроса устанавливает признак правильного ответа
        if not hasattr(self, 'correct_answer'):
            answer.correct_for_question = self
        elif self.correct_answer == answer:
            answer.correct_for_question = None
        else:
            old_correct_answer = self.correct_answer
            old_correct_answer.correct_for_question = None
            old_correct_answer.save()
            answer.correct_for_question = self
        answer.save()


class Tag(models.Model):
    name = models.SlugField(unique=True)
    question = models.ManyToManyField(Question, related_name='related_tags')


class Answer(Entity):
    author = models.ForeignKey(get_user_model(), related_name='answers',
                               on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers',
                                 on_delete=models.CASCADE)
    correct_for_question = models.OneToOneField(Question, related_name='correct_answer',
                                                null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-rating", "-pub_date"]

    def set_author(self, user):
        self.author = user

    def __str__(self):
        return 'answer-{}'.format(str(self.pk))


class Votes(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    vote_type = models.IntegerField()
    question = models.ForeignKey('Question', null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', null=True, blank=True, on_delete=models.CASCADE)
