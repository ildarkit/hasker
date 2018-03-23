from django.test import TestCase

from ..models import Profile


class ProfileTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'username':'user',
                         'email': 'user@testcase.com',
                         'password': 'User#123*test'}

    def test_create_user(self):
        user = Profile.objects.create_user(self.user_data)

        self.assertTrue(Profile.objects.filter(username=self.user_data['username']).exists(),
                        "User was not created.")




