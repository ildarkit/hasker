from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist


class Profile(AbstractUser):
    icon = models.ImageField('avatar', blank=True)
    registration = models.DateTimeField('date registration', default=timezone.now)

    def answer_voting(self, question, answer, vote_type):
        """ Голосование за ответ"""
        up_voted_answer = question.answers.filter(up_votes=self)
        down_voted_answer = question.answers.filter(down_votes=self)

        if 'up' in vote_type and not up_voted_answer:
            if not down_voted_answer:
                # голосуем "вверх", если нет голоса "вниз"
                answer.rating += 1
                answer.up_votes.add(self)
            elif answer in down_voted_answer:
                # отмена своего голоса пользователем
                answer.rating += 1
                answer.down_votes.remove(self)

        elif 'down' in vote_type and not down_voted_answer:
            if not up_voted_answer:
                # голосуем "вниз", если нет голоса "вверх"
                answer.rating -= 1
                answer.down_votes.add(self)
            elif answer in up_voted_answer:
                # отмена своего голоса пользователем
                answer.rating -= 1
                answer.up_votes.remove(self)

        answer.save()

    def set_correct_answer(self, question, answer):
        # Автор вопроса устанавливает признак правильного ответа
        try:
            already_incorrect_answer = question.answers.get(is_correct=True)
        except ObjectDoesNotExist:
            already_incorrect_answer = None
        if already_incorrect_answer and already_incorrect_answer != answer:
            already_incorrect_answer.is_correct = False
            already_incorrect_answer.save()
        answer.is_correct = not answer.is_correct

        answer.save()

    def question_voting(self, question, vote_type):
        """ Голосование за вопрос"""
        up_voted = question.up_votes.filter(profile_id=self.pk)
        down_voted = question.down_votes.filter(profile_id=self.pk)

        if 'up' in vote_type and not up_voted:
            question.rating += 1
            if not down_voted:
                # голосуем "вверх", если нет голоса "вниз"
                question.up_votes.add(self)
            else:
                # отмена своего голоса пользователем
                question.down_votes.remove(self)

        elif 'down' in vote_type and not down_voted:
            question.rating -= 1
            if not up_voted:
                # голосуем "вниз", если нет голоса "вверх"
                question.down_votes.add(self)
            else:
                # отмена своего голоса пользователем
                question.up_votes.remove(self)

        question.save()
