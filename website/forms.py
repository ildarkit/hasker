from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Question
from .models import HaskerUser


class QuestionCreateForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['header', 'text', 'tags']


class UserCreateForm(UserCreationForm):

    class Meta:
        model = HaskerUser
        fields = ['username', 'email', 'password1', 'password2', 'icon']
