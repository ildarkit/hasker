from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from ..models import Profile
from ..views import login_view, settings_view, signup_view


class UserTestCase(TestCase):

    def setUp(self):
        pass

    def test_login(self):
        pass

    def test_signup(self):
        pass

    def test_settings(self):
        pass
