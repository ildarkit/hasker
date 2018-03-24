from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from website.qa.models import Question


def cases(test_cases):
    def decorator(method):
        def wrapper(self):
            for test in test_cases:
                method(self, test)

        return wrapper

    return decorator


class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user',
                     'email': 'user@testcase.com',
                     'password': 'User#123*test'}
        user = get_user_model().objects.create_user(user_data)

        questions = Question.objects.bulk_create([
            Question(header='Question', slug='question-1',
                     text='tests fail', author=user, tags='python, tests, unit'),
            Question(header='question hasker', slug='question-2',
                     text='teST of question', author=user, tags='py3, rocket,'),
            Question(header='request error ', slug='question-3',
                     text='text of question', author=user, tags='user, django, login'),
            Question(header='module test', slug='question-6',
                     text='text of question', author=user, tags='module, request'),
            Question(header='unit tEstS', slug='question-10',
                     text='text of question', author=user, tags='tests, go, py'),
            Question(header='data science question', slug='question-13',
                     text='text of question', author=user, tags='error, template, render'),
            Question(header='how run tesTS', slug='question-7',
                     text='text of question', author=user, tags='python, django, web'),
            ]
        )
        questions[0].add_question_tags()
        questions[1].add_question_tags()
        questions[2].add_question_tags()
        questions[3].add_question_tags()
        questions[4].add_question_tags()
        questions[5].add_question_tags()
        questions[6].add_question_tags()

    @cases([
        ('TeSt', 5),
        ('DATA', 1),
        ('py', 0),
        ('error', 1),
        ('TExT', 5)
    ])
    def test_search_by_text(self, args):
        response = self.client.get('{}?q={}'.format(reverse('search'), args[0]))
        self.assertTrue(len(response.context['questions']) == args[1])

    @cases([
        ('pytHon', 2),
        ('PY', 1),
        ('DJANGO', 2),
        ('TeST', 0),
        ('Web', 1)
    ])
    def test_search_by_tag(self, args):
        response = self.client.get(reverse('tag_search', args=(args[0], )))
        self.assertTrue(len(response.context['questions']) == args[1])