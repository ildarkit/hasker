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
        tags = set(tags.strip(sep).lower().split(sep))
        tags = sep.join(map(str.strip, tags))
        return tags

    def set_question(self, request):
        question = None
        if self.is_valid():
            question = self.save(commit=False)
            question.set_author(request.user)
            question.add_question_tags()
        return question


class AnswerCreateForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('text', )

    def set_answer(self, request):
        answer = None
        if self.is_valid():
            answer = self.save(commit=False)
            answer.set_author(request.user)
        return answer
