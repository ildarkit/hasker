from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from ..models import Question, Answer
from ..views import page_404_view, vote_view, question_list_view, answer_view, question_view


def cases(test_cases):
    def decorator(method):
        def wrapper(self):
            for test in test_cases:
                method(self, test)

        return wrapper

    return decorator


class TestViewsCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'question_author',
                     'email': 'question_author@testcase.com',
                     'password': 'User#123*test'}
        cls.question_author = get_user_model().objects.create_user(user_data)
        cls.voter = get_user_model().objects.create_user({'username': 'voter',
                                                          'email': 'question_voter@testcase.com',
                                                          'password': 'User#123*test'})
        cls.answer_author = get_user_model().objects.create_user({'username': 'answer_author',
                                                                  'email': 'answer_author@testcase.com',
                                                                  'password': 'User#123*test'})

        questions = Question.objects.bulk_create([
            Question(header='Question', slug='question-1',
                     text='tests fail', author=cls.question_author, tags='python, tests, unit'),
            Question(header='question hasker', slug='question-2',
                     text='teST of question', author=cls.question_author, tags='py3, rocket,'),
            Question(header='request error ', slug='question-3',
                     text='text of question', author=cls.question_author, tags='user, django, login'),
            Question(header='module test', slug='question-6',
                     text='text of question', author=cls.question_author, tags='module, request'),
            Question(header='unit tEstS', slug='question-10',
                     text='text of question', author=cls.question_author, tags='tests, go, py'),
            Question(header='data science question', slug='question-13',
                     text='text of question', author=cls.question_author, tags='error, template, render'),
            Question(header='how run tesTS', slug='question-7',
                     text='text of question', author=cls.question_author, tags='python, django, web'),
        ])
        questions[0].add_question_tags()
        questions[1].add_question_tags()
        questions[2].add_question_tags()
        questions[3].add_question_tags()
        questions[4].add_question_tags()
        questions[5].add_question_tags()
        questions[6].add_question_tags()

        cls.answers = Answer.objects.bulk_create([
            Answer(author=cls.answer_author, text='answer text', question=questions[3]),
            Answer(author=cls.answer_author, text='answer text', question=questions[1]),
            Answer(author=cls.answer_author, text='answer text', question=questions[5]),
            Answer(author=cls.answer_author, text='answer text', question=questions[6]),
        ])

        cls.from_question = questions[0]

    def setUp(self):
        self.request_factory = RequestFactory()

    @cases(('/index/', '/question/', '/answer/',
            '/question/-question-/', '263%$@!#!@#*()',
            '/vote/', '/question/../../', '.', '-', '//#%$#/'))
    def test_not_found(self, args):
        """ Страница не найдена """
        request = self.request_factory.get(args)
        request.session = self.client.session
        response = page_404_view(request)
        self.assertEqual(response.status_code, 404)

    @cases((  # (slug, vote_type, result_rating)
            ('question-1', '1', '1'),
            ('question-2', '-1', '-1'),
            ('question-1', '1', '0'),
            ('question-2', '-1', '0'),
    ))
    def test_question_vote(self, args):
        """ Голосование за вопрос"""
        request = self.request_factory.post(reverse('vote', args=args[:-1]))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args[:-1])
        question = Question.objects.get(slug=args[0])

        self.assertEqual(question.rating, int(args[-1]))

    def test_answer_vote(self):
        """ Голосование за ответы"""
        #  голос вверх
        answer = self.answers[0]
        args = (str(answer.question), '1', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertEqual(after_vote_answer.rating, int(args[1]))

        # голос вниз
        answer = self.answers[1]
        args = (str(answer.question), '-1', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertEqual(after_vote_answer.rating, int(args[1]))

        # отмена голоса
        # не важно вверх или вниз
        # еще один голос отменяет его
        answer = self.answers[0]
        args = (str(answer.question), '1', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertEqual(after_vote_answer.rating, 0)

        # отмена голоса
        # не важно вверх или вниз
        # еще один голос отменяет его
        answer = self.answers[1]
        args = (str(answer.question), '-1', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertEqual(after_vote_answer.rating, 0)

    def test_correct_answer_vote(self):
        """ Выбор правильного ответа"""
        answer = self.answers[2]
        args = (str(answer.question), 'correct', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertEqual(after_vote_answer.correct_for_question, answer.question)

        # теперь другой ответ правильный
        answer = self.answers[3]
        args = (str(answer.question), 'correct', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertEqual(after_vote_answer.correct_for_question, answer.question)

        # отмена признака правильного ответа
        answer = self.answers[3]
        args = (str(answer.question), 'correct', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = self.voter
        _ = vote_view(request, *args)
        after_vote_answer = Answer.objects.get(pk=answer.pk)
        self.assertIsNone(after_vote_answer.correct_for_question)

    def test_answer_vote_anonymous(self):
        """ Анонимные пользователи не голосуют """
        answer = self.answers[0]
        args = (str(answer.question), '1', str(answer))
        request = self.request_factory.post(reverse('vote', args=args))
        request.session = self.client.session
        request.user = AnonymousUser()
        response = vote_view(request, *args)
        self.assertEqual(response.status_code, 302)  # редирект на страницу входа

    def test_question_list(self):
        """ Список вопросов """
        request = self.request_factory.get(reverse('ask'))
        request.session = self.client.session
        response = question_list_view(request)
        self.assertEqual(response.status_code, 200)

    @cases((
            ('question-2', 2),
            ('question-3', 1),
    ))
    def test_answer(self, args):
        """ Создание ответа """
        request = self.request_factory.post(reverse('answer', args=args[:-1]),
                                            {'text': 'answer for {}'.format(args[0])}
                                            )
        request.session = self.client.session
        request.user = self.answer_author
        _ = answer_view(request, args[0])
        question = Question.objects.get(slug=args[0])
        self.assertEqual(question.answers.count(), args[1])
        self.assertTrue(
            question.answers.filter(text='answer for {}'.format(args[0])).exists()
        )

    @cases((
            'question-1', 'question-2', 'question-3', 'question-6', 'question-7', 'question-10', 'question-13',
    ))
    def test_question_detail(self, args):
        """ Страница вопроса """
        request = self.request_factory.get(reverse('question', args=[args]))
        request.session = self.client.session
        request.user = AnonymousUser()
        response = question_view(request, args)
        self.assertEqual(response.status_code, 200)

    @cases((
            'question-4', 'question-5', 'question-8', 'question-9', 'question-11', 'question-12',
    ))
    def test_question_detail_not_found(self, args):
        """ Вопрос не найден """
        request = self.request_factory.get(reverse('question', args=[args]))
        request.session = self.client.session
        request.user = AnonymousUser()
        response = question_view(request, args)
        self.assertEqual(response.status_code, 404)

    def test_create_question(self):
        """ Создание вопроса и переход на страницу вопроса"""
        question = Question(header='Question', slug='question-18',
                            text='tests fail', author=self.question_author, tags='python, tests, unit')
        question.save()
        question.add_question_tags()
        request = self.request_factory.post(reverse('question', args=[str(question)]))
        request.session = self.client.session
        # мы как будто находились на странице вопроса self.from_question
        request.session['question_id'] = str(self.from_question.pk)
        request.user = self.question_author
        response = question_view(request, str(question))
        self.assertEqual(response.status_code, 200)