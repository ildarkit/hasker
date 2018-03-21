import urllib
from os.path import join

from django.db import transaction
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout

from .forms import UserForm, LoginUserForm, UserCreateForm

from website.qa.helpers import render_or_redirect_question


def login_view(request):
    """ Страница авторизации """

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

    return render_or_redirect_question(request, 'profiles/login.html',
                                       {'login_form': login_form})


def logout_view(request):
    logout(request)
    return redirect('ask')


@transaction.atomic
def signup_view(request):
    """ Страница регистрации """

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

    return render_or_redirect_question(request, 'profiles/signup.html',
                                       {'user_form': user_form})


@transaction.atomic
def settings_view(request):
    """ Страница настроек пользователя """
    if request.user.is_authenticated:

        if request.method == 'POST':
            user_form = UserForm(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('ask')
            elif len(user_form.fields & request.POST.keys()) != len(user_form.fields):
                # запрос не для этой формы, т.к. нет совпадения по полям
                # восстанавливаем пустую форму
                user_form = UserForm(instance=request.user)

        elif request.method == 'GET':
            user_form = UserForm(instance=request.user)

        return render_or_redirect_question(request, 'profiles/settings.html',
                                           {'user_form': user_form})

    else:
        return redirect('ask')


def get_user_icon_view(request):
    path = join(settings.MEDIA_ROOT, request.user.icon.url)
    path = urllib.parse.unquote(path)
    return FileResponse(
        open(path, "rb")
    )
