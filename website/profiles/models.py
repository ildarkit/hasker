from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


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
        if not hasattr(question, 'correct_answer'):
            answer.correct_for_question = question
        elif question.correct_answer == answer:
            answer.correct_for_question = None
        else:
            old_correct_answer = question.correct_answer
            old_correct_answer.correct_for_question = None
            old_correct_answer.save()
            answer.correct_for_question = question
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
