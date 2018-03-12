from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist

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

    def answer_voting(self, user, answer, vote_type):
        up_voted_answer = self.answers.filter(up_votes=user)
        down_voted_answer = self.answers.filter(down_votes=user)

        if 'up' in vote_type and not up_voted_answer:
            if not down_voted_answer:
                # голосуем "вверх", если нет голоса "вниз"
                answer.rating += 1
                answer.up_votes.add(user)
            elif answer in down_voted_answer:
                # отмена своего голоса пользователем
                answer.rating += 1
                answer.down_votes.remove(user)

        elif 'down' in vote_type and not down_voted_answer:
            if not up_voted_answer:
                # голосуем "вниз", если нет голоса "вверх"
                answer.rating -= 1
                answer.down_votes.add(user)
            elif answer in up_voted_answer:
                # отмена своего голоса пользователем
                answer.rating -= 1
                answer.up_votes.remove(user)

        answer.save()

    def set_correct_answer(self, answer):
        # автор вопроса устанавливает признак правильного ответа
        try:
            already_incorrect_answer = self.answers.get(is_correct=True)
        except ObjectDoesNotExist:
            already_incorrect_answer = None
        if already_incorrect_answer and already_incorrect_answer != answer:
            already_incorrect_answer.is_correct = False
            already_incorrect_answer.save()
        answer.is_correct = not answer.is_correct

        answer.save()

    def voting(self, user, vote_type):
        up_voted = self.up_votes.filter(pk=user.pk)
        down_voted = self.down_votes.filter(pk=user.pk)

        if 'up' in vote_type and not up_voted:
            self.rating += 1
            if not down_voted:
                # голосуем "вверх", если нет голоса "вниз"
                self.up_votes.add(user)
            else:
                # отмена своего голоса пользователем
                self.down_votes.remove(user)

        elif 'down' in vote_type and not down_voted:
            self.rating -= 1
            if not up_voted:
                # голосуем "вниз", если нет голоса "вверх"
                self.down_votes.add(user)
            else:
                # отмена своего голоса пользователем
                self.up_votes.remove(user)

        self.save()

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
        ordering = ["-rating", "-pub_date"]
