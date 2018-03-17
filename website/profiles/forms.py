from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.files.images import get_image_dimensions

from .models import Profile
from .admin import UserCreationForm


class UserCreateForm(UserCreationForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError(_("Please fill in this field."))
        else:
            return email

    def clean_icon(self):
        avatar = self.cleaned_data['icon']
        w, h = get_image_dimensions(avatar)
        max_width = max_height = 100
        if w > max_width or h > max_height:
            raise forms.ValidationError(
                u'Please use an image that is '
                '%s x %s pixels or smaller.' % (max_width, max_height))

        # validate content type
        main, sub = avatar.content_type.split('/')
        if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
            raise forms.ValidationError(u'Please use a JPEG, '
                                        'GIF or PNG image.')

        # validate file size
        if len(avatar) > (20 * 1024):
            raise forms.ValidationError(
                u'Avatar file size may not exceed 20k.')

        return avatar


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
