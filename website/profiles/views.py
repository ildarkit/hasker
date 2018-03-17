from os.path import join

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .forms import UserForm, LoginUserForm, UserCreateForm

from website.helpers import create_question_form_helper


def login_view(request):
    """ Страница авторизации """
    tags = ()
    question_form = ()
    if request.user.is_authenticated:
        # Форма задавания вопроса на странице авторизации
        question_helper = create_question_form_helper(request)
        question_form = question_helper.question_form
        question = question_helper.question
        tags = question_helper.tags
        if question_form.is_bound and question:
            return redirect('question', str(question))

    if request.method == 'GET':
        login_form = LoginUserForm()
    elif request.method == 'POST':
        login_form = LoginUserForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('ask')
    return render(request, 'profiles/login.html', context={'form': question_form, 'tags': tags,
                                                  'login_form': login_form})


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
        user_form = UserCreateForm(request.POST, request.FILES)
        if user_form.is_valid():
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = user_form.save()
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('ask')

    elif request.method == 'GET':
        user_form = UserCreateForm()
    return render(request, 'profiles/signup.html', {'user_form': user_form,
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

            user_form = UserForm(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('ask')
        elif request.method == 'GET':
            user_form = UserForm(instance=request.user)
        return render(request, 'profiles/settings.html', {'user_form': user_form,
                                                 'form': question_helper.question_form,
                                                 'tags': question_helper.tags, })
    else:
        return redirect('ask')


def get_user_icon_view(request):
    image_data = open(join(settings.MEDIA_ROOT, request.user.icon.url), "rb").read()
    return HttpResponse(image_data, content_type="image")
