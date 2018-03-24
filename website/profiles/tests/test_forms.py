from django.test import TestCase

from ..models import Profile
from ..forms import UserCreateForm, UserForm, LoginUserForm


class UserFormsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = Profile.objects.create_user(username='user',
                                               email='user@haskertest.com',
                                               password='User#123*test')

    def test_signup_form(self):
        form = UserCreateForm({'username': 'another_user',
                               'email': self.user.email,
                               'password1': self.user.password,
                               'password2': self.user.password, })
        self.assertTrue(form.is_valid())

    def test_signup_form_fail(self):
        form = UserCreateForm({'username': 'another_user1',
                               'email': 'email@email',
                               'password1': self.user.password,
                               'password2': self.user.password, })
        self.assertFalse(form.is_valid())

    def test_login_form(self):
        form = LoginUserForm({'username':  self.user.username,
                              'password': self.user.password, })
        self.assertTrue(form.is_valid())

    def test_settings_form(self):
        form = UserForm({'email': 'modify@haskertest.com', 'icon': ''},
                        instance=self.user)
        _ = form.is_valid()
        self.assertEqual(form.cleaned_data['email'], 'modify@haskertest.com')

    def test_settings_form_fail(self):
        form = UserForm({'email': 'modify@haskertest', 'icon': ''},
                        instance=self.user)
        form.is_valid()
        self.assertFalse(form.is_valid())

    def test_clean_username_false(self):
        form = UserCreateForm({
            'username': self.user.username,
            'password1': 'notalamodespassword',
            'password2': 'notalamodespassword',
        })
        _ = form.is_valid()
        self.assertTrue('username' in form.errors)
