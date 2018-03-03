from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import Question
from .models import Profile


class QuestionCreateForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('header', 'text', 'tags', )


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class ProfileCreateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('icon', )
