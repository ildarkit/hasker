from django import forms

from .models import Answer
from .models import Question


class QuestionCreateForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('header', 'text', 'tags', )

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        sep = ', '
        tags = set(tags.strip(sep).split(sep))
        tags = sep.join(map(str.strip, tags))
        return tags


class AnswerCreateForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('answer_text', )