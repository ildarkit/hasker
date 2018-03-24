from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from ..views import login_view, settings_view, signup_view


class UserTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='user',
                                               email='user@haskertest.com',
                                               password='User#123*test')

    def setUp(self):
        self.user_data = {'username': 'another_user', 'password1': 'strongPass123#',
                          'password2': 'strongPass123#', 'email': 'another@haskertest.com'}
        self.request_factory = RequestFactory()

    def test_login(self):
        request = self.request_factory.post(reverse('login'),
                                            {'username': 'user', 'password': 'User#123*test'}
                                            )
        request.session = self.client.session
        # request.user = AnonymousUser()
        response = login_view(request)
        self.assertEqual(response.status_code, 302)  # редирект, залогинились

    def test_login_fail(self):
        request = self.request_factory.post(reverse('login'),
                                            {'username': 'unknown', 'password': 'password#!1234'})
        request.user = AnonymousUser()
        response = login_view(request)
        self.assertEqual(response.status_code, 200)  # редиректа не случилось

    def test_signup(self):
        request = self.request_factory.post(reverse('signup'), self.user_data)
        request.session = self.client.session
        response = signup_view(request)
        self.assertEqual(response.status_code, 302)  # редирект после регистрации

    def test_modify_settings(self):
        request = self.request_factory.post(reverse('settings'), {'email': 'modifed_another@haskertest.com'})
        request.user = self.user
        _ = settings_view(request)
        user = get_user_model().objects.get(email='modifed_another@haskertest.com')
        self.assertTrue(user)
