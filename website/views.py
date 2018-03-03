from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory
from django.db.models import Prefetch
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from .models import Question
from .models import Answer
from .models import Profile
from .forms import QuestionCreateForm
from .forms import UserCreateForm
from .forms import ProfileCreateForm


def question_list_view(request):
    if request.method == 'POST':
        question_form = QuestionCreateForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.author = Profile.objects.get(pk=request.user.pk)
            question.save()
            request.session['question_id'] = str(question.pk)
            return redirect('question', str(question))
    else:
        question_form = QuestionCreateForm()
    questions = Question.objects.all()
    return render(request, 'list.html', {'form': question_form, 'questions': questions})


def search(request):
    pass


def index(request):
    return redirect('ask')


def question(request, header):
    question_id = request.session.pop('question_id', None)
    if question_id:
        question_query = Question.objects.filter(pk=question_id)
    else:
        header = header.replace('-', ' ')
        question_query = Question.objects.filter(header=header)
    if request.method == 'GET':
        question_form = QuestionCreateForm()
        return render(request, 'question.html',
                      context={'questions': question_query, 'form': question_form})
    else:
        return question_list_view(request)


def tag(request):
    pass


def logout_view(request):
    logout(request)
    return redirect('ask')


def signup_view(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        profile_form = ProfileCreateForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = user_form.save()
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, _('Welcome to Hasker, {}'.format(username)))
            return redirect('ask')

    else:
        user_form = UserCreateForm()
        profile_form = ProfileCreateForm()
    return render(request, 'signup.html', {
        'user_form': (user_form, profile_form)
    })


def settings(request):
    pass

