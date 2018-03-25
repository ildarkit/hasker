from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..models import Question, Answer, Votes, Tag


def cases(test_cases):
    def decorator(method):
        def wrapper(self):
            for test in test_cases:
                method(self, test)

        return wrapper

    return decorator


class TestModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='user',
                                                        email='user@haskertest.com',
                                                        password='User#123*test')
        cls.answer_author = get_user_model().objects.create_user(username='answer_author',
                                                                 email='answer_author@haskertest.com',
                                                                 password='User#123*test')
        cls.question = Question(author=cls.user, header='question tests title',
                                text='question test body', tags='python, tests, unit', slug='question-1')
        cls.question.save()

        cls.answer = Answer(author=cls.answer_author, text='answer text test', question=cls.question)
        cls.answer.save()

    def test_question_model_create(self):
        question = Question(author=self.user, header='question tests title',
                            text='question test body', tags='python, django, web', slug='question-9')
        question.save()
        self.assertTrue(Question.objects.filter(slug='question-9').exists())

    @cases((
            {'header': '',
             'text': '',
             'tags': ''},
            {'header': '',
             'text': 'question text',
             'tags': 'py3, django, tests'},
            {'header': 'question for tests',
             'text': '',
             'tags': 'py3, django, tests'},
            {'header': 'question for tests',
             'text': 'question text',
             'tags': 'py3, django, tests, more'},
            {'header': 'question for tests',
             'text': 'question text',
             'tags': 'py3, django-tests, '}
    ))
    def test_question_model_create_fail(self, kwargs):
        kwargs['author'] = self.user
        question = Question(**kwargs)
        self.assertRaises(ValidationError, question.full_clean)

    def test_set_correct_answer(self):
        self.question.set_correct_answer(self.answer)
        self.assertTrue(self.question.correct_answer == self.answer)

    def test_tags_create(self):
        self.question.add_question_tags()
        tag_list = self.question.tags_as_list()
        tags = list(Tag.objects.values_list('name', flat=True))
        self.assertTrue(tag_list == tags)

    def test_answer_model_create(self):
        answer = Answer(author=self.answer_author, text='answer test text', question=self.question)
        answer.save()
        self.assertTrue(Answer.objects.filter(
            author=self.answer_author, text='answer test text', question=self.question
        ).exists())

    def test_answer_model_create_fail(self):
        answer = Answer(author=self.answer_author, text='', question=self.question)
        self.assertRaises(ValidationError, answer.full_clean)

    def test_vote_for_answer_model_create(self):
        vote = Votes(user=self.user, vote_type=-1, answer=self.answer)
        vote.save()
        self.assertTrue(Votes.objects.filter(
            user=self.user, vote_type=-1, answer=self.answer
        ).exists())

    def test_vote_for_question_model_create(self):
        vote = Votes(user=self.answer_author, vote_type=-1, question=self.question)
        vote.save()
        self.assertTrue(Votes.objects.filter(
            user=self.answer_author, vote_type=-1, question=self.question
        ).exists())

    def test_question_vote_method(self):
        self.question.vote(self.answer_author, 1)
        self.assertTrue(Votes.objects.filter(
            user=self.answer_author, vote_type=1, question=self.question
        ).exists())

    def test_answer_vote_method(self):
        self.answer.vote(self.user, 1)
        self.assertTrue(Votes.objects.filter(
            user=self.user, vote_type=1, answer=self.answer
        ).exists())
