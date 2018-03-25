from django.test import TestCase

from ..forms import QuestionCreateForm, AnswerCreateForm


def cases(test_cases):
    def decorator(method):
        def wrapper(self):
            for test in test_cases:
                method(self, test)

        return wrapper

    return decorator


class TestForms(TestCase):

    def test_question_form(self):
        form = QuestionCreateForm({'header': 'question for tests',
                                   'text': 'question text',
                                   'tags': 'py3, django, tests'})

        self.assertTrue(form.is_valid())

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
    def test_question_form_invalid(self, kwargs):
        form = QuestionCreateForm(kwargs)

        self.assertFalse(form.is_valid())

    def test_answer_form(self):
        form = AnswerCreateForm({'text': 'answer text'})
        self.assertTrue(form.is_valid())

    def test_answer_form_invalid(self):
        form = AnswerCreateForm({'text': ''})
        self.assertFalse(form.is_valid())
