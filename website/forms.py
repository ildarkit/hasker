from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import Answer
from .models import Question
from .models import Profile


class QuestionCreateForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('header', 'text', 'tags', )

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        sep = ', '
        tags = set(tags.strip(sep).split(sep))
        tags = sep.join(tags)
        return tags


class AnswerCreateForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('answer_text', )


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError(_("Please fill in this field."))
        else:
            return email


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError(_("Please fill in this field."))
        else:
            return email


class ProfileCreateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('icon', )
