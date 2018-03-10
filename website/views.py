from collections import namedtuple

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Tag
from .models import Question
from .models import Answer
from .models import Profile
from .forms import UserForm
from .forms import LoginUserForm
from .forms import AnswerCreateForm
from .forms import QuestionCreateForm
from .forms import UserCreateForm
from .forms import ProfileCreateForm


def render_404_page(request):
    question_helper = create_question_form_helper(request)
    if request.method == 'POST':
        return redirect('question', str(question_helper.question))
    return render(request, '404.html',
                  context={'form': question_helper.question_form,
                           'tags': question_helper.tags})


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
        try:
            tag = Tag.objects.get(name=tag_name)
        except ObjectDoesNotExist:
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
    sorting = request.GET.get('sorting', None) or request.session.get('sorting', None)
    if sorting:
        if sorting == 'date':
            sort = '-pub_date'
        else:
            sort = 'rating'
        request.session['sorting'] = sorting
    else:
        sort = '-pub_date'
    questions = questions.order_by(sort)

    page = request.GET.get('page', None) or request.session.get('questions_page', None)
    if page:
        request.session['questions_page'] = page
    else:
        page = 1
    paginator = Paginator(questions, 4)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    return render(request, 'list.html', context={'questions': questions,
                                                 'form': question_helper.question_form,
                                                 'tags': question_helper.tags})


def search(request):
    pass


def index(request):
    if request.path != '/':
        return render_404_page(request)
    else:
        return redirect('ask')


def answer_view(request):
    """
    Валидация формы ответа, сохранение ответа, связанного с вопросом.
    Редирект на страницу вопроса.
    """
    if request.user.is_authenticated:
        answer_helper = create_answer_form_helper(request)
        answer = answer_helper.answer
        answer_form = answer_helper.answer_form
    else:
        answer_form = ()

    if request.method == 'POST' and answer_form and answer_form.is_bound:
        question_id = request.GET.get('question_id', None)
        question = Question.objects.get(pk=int(question_id))
        answer.question = question
        answer.save()
        request.session['updated_question_id'] = str(question.pk)
        return redirect('question', str(question))
    elif request.method == 'GET':
        return render_404_page(request)


def question_view(request, header):
    """ Страница вопроса со списком ответов """
    question_helper = create_question_form_helper(request)
    question_form = question_helper.question_form
    answers = ()
    if request.user.is_authenticated:
        answer_form = AnswerCreateForm()
    else:
        answer_form = ()

    if request.method == 'GET':
        new_question_id = request.session.pop('new_question_id', None)
        updated_question_id = request.session.pop('updated_question_id', None)
        if new_question_id:
            # Новый вопрос
            question = Question.objects.get(pk=int(new_question_id))
            request.session['question_id'] = new_question_id
        elif updated_question_id:
            question = Question.objects.get(pk=int(updated_question_id))
        else:
            # Попытка найти вопрос по его заголовку, полученному из строки запроса.
            header = header.replace('-', ' ')
            try:
                question = Question.objects.get(header=header)
            except ObjectDoesNotExist:
                return render_404_page(request)
            else:
                request.session['question_id'] = str(question.pk)

        # Пагинация ответов на странице вопроса по 30 шт.
        page = request.GET.get('page', None) or request.session.get('answers_page', None)
        if page:
            request.session['answers_page'] = page
        else:
            page = 1
        answers = question.answers.all()
        paginator = Paginator(answers, 4)
        try:
            answers = paginator.page(page)
        except PageNotAnInteger:
            answers = paginator.page(1)
        except EmptyPage:
            answers = paginator.page(paginator.num_pages)

    elif request.method == 'POST':
        if question_form.is_bound:
            # переход на страницу созданного вопроса
            question = question_helper.question
            request.session['new_question_id'] = str(question.pk)
            return redirect('question', str(question))

    return render(request, 'question.html',
                  context={'question': question,
                           'form': question_form,
                           'answer_form': answer_form,
                           'answers': answers,
                           'tags': question_helper.tags})


@login_required
def vote_view(request):
    question_id = int(request.GET['question_id'])
    question = Question.objects.get(pk=question_id)
    for key in ('up_vote', 'down_vote', 'up_answer_id', 'down_answer_id'):
        obj_id = request.GET.get(key, None)
        if obj_id:
            obj = Answer if 'answer' in key else Question
            if 'up' in key:
                vote_helper(request, obj=obj, up_vote_id=obj_id)
            else:
                vote_helper(request, obj=obj, down_vote_id=obj_id)
            
    request.session['updated_question_id'] = str(question.pk)
    return redirect('question', str(question))


def vote_helper(request, obj, up_vote_id=None, down_vote_id=None):
    vote_id = up_vote_id or down_vote_id
    db_object = obj.objects.get(pk=int(vote_id))
    if up_vote_id:
        voted = db_object.up_votes.filter(username=request.user.username)
    else:
        voted = db_object.down_votes.filter(username=request.user.username)
    if not voted:
        if up_vote_id:
            db_object.up_votes.add(request.user)
            db_object.rating += 1
        else:
            db_object.down_votes.add(request.user)
            db_object.rating -= 1
        db_object.save()


def tag(request):
    pass


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
    return render(request, 'login.html', context={'form': question_form, 'tags': tags,
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
        user_form = UserCreateForm(request.POST)
        profile_form = ProfileCreateForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = user_form.save()
            user = authenticate(username=username, password=raw_password)
            login(request, user)
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

