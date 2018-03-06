from collections import namedtuple

from django.http import Http404
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

from .models import Tag
from .models import Question
from .models import Answer
from .models import Profile
from .forms import UserForm
from .forms import AnswerCreateForm
from .forms import QuestionCreateForm
from .forms import UserCreateForm
from .forms import ProfileCreateForm


def create_question_form_helper(request):
    """ Вспомогательная функция создания формы вопроса"""
    tags = []
    question = None
    question_form = None
    if request.method == 'POST':
        question_form = QuestionCreateForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.author = Profile.objects.get(user_id=request.user.pk)
            question.save()
            add_question_tags(question)
            request.session['new_question_id'] = str(question.pk)
    elif request.method == 'GET':
        tags = Tag.objects.all()
        question_form = QuestionCreateForm()
    QuestionHelper = namedtuple('QuestionHelper', ('question_form', 'question', 'tags'))
    return QuestionHelper(question_form, question, tags)


def add_question_tags(question):
    related_tags = []
    for tag_name in question.tags.split(','):
        tag_name = tag_name.strip()
        tag = Tag.objects.get(name=tag_name)
        if not tag:
            tag = Tag.objects.create(name=tag_name)
        related_tags.append(tag)
    question.related_tags.add(*related_tags)


def create_answer_form_helper(request):
    """ Вспомогательная функция создания формы ответа"""
    answer = None
    answer_form = None
    if request.method == 'POST':
        answer_form = AnswerCreateForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.author = Profile.objects.get(user_id=request.user.pk)
            answer.save()
    elif request.method == 'GET':
        answer_form = AnswerCreateForm()
    AnswerHelper = namedtuple('AnswerHelper', ('answer_form', 'answer'))
    return AnswerHelper(answer_form, answer)


def question_list_view(request):
    """Главная страница со списком вопросов"""
    question_helper = create_question_form_helper(request)
    question = question_helper.question
    if request.method == 'POST' and question:
        return redirect('question', str(question))
    questions = Question.objects.all()
    return render(request, 'list.html', context={'questions': questions,
                                                 'form': question_helper.question_form,
                                                 'tags': question_helper.tags})


def search(request):
    pass


def index(request):
    return redirect('ask')


def question_view(request, header):
    """ Страница вопроса со списком ответов """
    question_helper = create_question_form_helper(request)
    question_form = question_helper.question_form
    answer_helper = create_answer_form_helper(request)

    if request.method == 'GET':
        new_question_id = request.session.pop('new_question_id', None)
        if new_question_id:
            # Новый вопрос
            question = Question.objects.get(pk=new_question_id)
        else:
            # Попытка найти вопрос по его заголовку, полученному из строки запроса.
            question_id = request.session.pop('question_id', None)
            if question_id:
                question = Question.objects.get(pk=question_id)
            else:
                header = header.replace('-', ' ')
                question = Question.objects.get(header=header)
            if not question:
                raise Http404("No question match the given query.")

    elif request.method == 'POST':
        if question_form.is_bound():
            # переход на страницу созданного вопроса
            question = question_helper.question
            request.session['new_question_id'] = str(question.pk)
            return redirect('question', str(question))
        elif answer_helper.answer_form.is_bound():
            # создан ответ
            question_id = request.session.get('question_id', None)
            question = Question.objects.get(pk=question_id)
            question.answers = answer_helper.answer
            question.save()

    return render(request, 'question.html',
                  context={'question': question,
                           'form': question_form,
                           'answer_form': answer_helper.answer_form,
                           'tags': question_helper.tags})


def tag(request):
    pass


def logout_view(request):
    logout(request)
    return redirect('ask')


def signup_view(request):
    """ Страница регистрации """
    question_form = ()
    tags = []
    if request.user.is_authenticated:
        # форма вопроса на странице регистрации
        question_helper = create_question_form_helper(request)
        question_form = question_helper.question_form
        question = question_helper.question
        tags = question_helper.tags
        if question_form.is_bound and question:
            return redirect('question', str(question))

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

    elif request.method == 'GET':
        user_form = UserCreateForm()
        profile_form = ProfileCreateForm()
    return render(request, 'signup.html', {'user_form': (user_form, profile_form),
                                           'form': question_form, 'tags': tags})


def settings_view(request):
    """ Страница настроек пользователя """
    if request.user.is_authenticated:
        question_helper = create_question_form_helper(request)
        if request.method == 'POST':
            # форма вопроса на странице настроек
            question = question_helper.question
            if question_helper.question_form.is_bound and question:
                return redirect('question', str(question))

            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileCreateForm(request.POST, instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return redirect('ask')
        elif request.method == 'GET':
            user = User.objects.get(pk=request.user.pk)
            profile = Profile.objects.get(user_id=request.user.pk)
            user_form = UserForm(instance=user)
            profile_form = ProfileCreateForm(instance=profile)
        return render(request, 'settings.html', {'user_form': (user_form, profile_form),
                                                 'form': question_helper.question_form,
                                                 'tags': question_helper.tags, })
    else:
        return redirect('ask')

