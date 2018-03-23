from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Profile
from .admin import UserCreationForm


class UserCreateForm(UserCreationForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError(_("Please fill in this field."))
        else:
            return email


class UserForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('email', 'icon', )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError(_("Please fill in this field."))
        else:
            return email


class LoginUserForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
