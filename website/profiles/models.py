from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist


class Profile(AbstractUser):
    icon = models.ImageField('avatar', upload_to='avatars/', blank=True)
    registration = models.DateTimeField('date registration', default=timezone.now)

    def answer_voting(self, question, answer, vote_type):
        """ Голосование за ответ"""
        up_voted_answer = question.answers.filter(pk=answer.pk).filter(up_votes=self)
        down_voted_answer = question.answers.filter(pk=answer.pk).filter(down_votes=self)

        if 'up' in vote_type and not up_voted_answer:
            if not down_voted_answer:
                # голосуем "вверх", если нет голоса "вниз"
                answer.rating += 1
                answer.up_votes.add(self)
            else:
                # отмена своего голоса пользователем
                answer.rating += 1
                answer.down_votes.remove(self)

        elif 'down' in vote_type and not down_voted_answer:
            if not up_voted_answer:
                # голосуем "вниз", если нет голоса "вверх"
                answer.rating -= 1
                answer.down_votes.add(self)
            else:
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

        up_voted_question = self.up_question_votes.filter(pk=question.pk)
        down_voted_question = self.down_question_votes.filter(pk=question.pk)

        if 'up' in vote_type and not up_voted_question:
            question.rating += 1
            if not down_voted_question:
                # голосуем "вверх", если нет голоса "вниз"
                question.up_votes.add(self)
            else:
                # отмена своего голоса пользователем
                question.down_votes.remove(self)

        elif 'down' in vote_type and not down_voted_question:
            question.rating -= 1
            if not up_voted_question:
                # голосуем "вниз", если нет голоса "вверх"
                question.down_votes.add(self)
            else:
                # отмена своего голоса пользователем
                question.up_votes.remove(self)

        question.save()
