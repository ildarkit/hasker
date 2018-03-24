from random import randint

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from website.qa.models import Question


class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_data = {'username': 'user',
                     'email': 'user@testcase.com',
                     'password': 'User#123*test'}
        cls.user = get_user_model().objects.create_user(user_data)
        tags = 'python, tests,unit'

        questions = Question.objects.bulk_create([
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            Question(header='Question' + str(randint(0, 100)), slug='question' + str(randint(0, 100)),
                     text='text of question' + str(randint(0, 100)), author=cls.user, tags=tags),
            ]
        )
        questions[0].add_question_tags()

    def test_search_by_text(self):
        response = self.client.get('{}?q=Quest'.format(reverse('search')))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Quest', response.context['questions'][0].header, )
        self.assertTrue(len(response.context['questions']) == 7)

    def test_search_by_tag(self):
        response = self.client.get(reverse('tag_search', args=['python']))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['questions']) == 7)