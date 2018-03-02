from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .models import Question
from .models import HaskerUser


class QuestionCreateForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['header', 'text', 'tags']

    def clean(self):
        cleaned_data = super(QuestionCreateForm, self).clean()
        if not cleaned_data:
            raise forms.ValidationError(_('Please fill all fields'))
        for field in cleaned_data:
            if not cleaned_data.get(field):
                self.add_error(field, forms.ValidationError(_('Please fill in this field')))


class UserCreateForm(UserCreationForm):

    class Meta:
        model = HaskerUser
        fields = ['username', 'email', 'password1', 'password2', 'icon']
