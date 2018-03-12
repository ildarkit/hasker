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

        answers = answer_pagination(request, question)

    elif request.method == 'POST':
        if question_form.is_bound:
            question = question_helper.question
            if question:
                # переход на страницу созданного вопроса
                request.session['new_question_id'] = str(question.pk)
                return redirect('question', str(question))
            else:
                # ошибка валидации формы вопроса
                # требуется восстановить вопрос, на странице которого
                # создавался новый вопрос
                question = Question.objects.get(pk=request.session['question_id'])
                answers = answer_pagination(request, question)

    return render(request, 'question.html',
                  context={'question': question,
                           'form': question_form,
                           'answer_form': answer_form,
                           'answers': answers,
                           'tags': question_helper.tags})


def answer_pagination(request, question):
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
    return answers


@login_required
def vote_view(request):
    question_id = request.GET.get('question_id')
    question = Question.objects.get(pk=question_id)
    votes = {'up_vote': request.GET.get('up_vote', None),
             'down_vote': request.GET.get('down_vote', None),
             'up_answer_id': request.GET.get('up_answer_id', None),
             'down_answer_id': request.GET.get('down_answer_id', None),
             'correct_answer_id': request.GET.get('correct_answer_id', None)
             }
    vote_helper(request, question, **votes)

    request.session['updated_question_id'] = str(question.pk)
    return redirect('question', str(question))


def vote_helper(request, question, **votes):
    up_voted = None
    down_voted = None
    vote_type = ''
    obj = question
    for key in votes:
        if votes[key]:
            vote_type = key
            if 'correct' in key:
                question = obj
                obj = Answer.objects.get(pk=votes[key])
            else:
                if 'answer' in key:
                    obj = Answer.objects.get(pk=votes[key])
                try:
                    up_voted = obj.up_votes.get(pk=request.user.pk)
                except ObjectDoesNotExist:
                    pass
                try:
                    down_voted = obj.down_votes.get(pk=request.user.pk)
                except ObjectDoesNotExist:
                    pass
            break

    if 'up' in vote_type and not up_voted:
        obj.rating += 1
        if not down_voted:
            # голосуем "вверх", если нет голоса "вниз"
            obj.up_votes.add(request.user)
        else:
            # отмена своего голоса пользователем
            obj.down_votes.remove(request.user)

    elif 'down' in vote_type and not down_voted:
        obj.rating -= 1
        if not up_voted:
            # голосуем "вниз", если нет голоса "вверх"
            obj.down_votes.add(request.user)
        else:
            # отмена своего голоса пользователем
            obj.up_votes.remove(request.user)

    elif 'correct' in vote_type:
        # автор вопроса устанавливает признак правильного ответа
        try:
            already_incorrect_answer = question.answers.get(is_correct=True)
        except ObjectDoesNotExist:
            already_incorrect_answer = None
        if already_incorrect_answer and already_incorrect_answer.pk != obj.pk:
            already_incorrect_answer.is_correct = False
            already_incorrect_answer.save()
        obj.is_correct = not obj.is_correct

    obj.save()


def tag_view(request, tag_name):
    """ Страница с результатами поиска по тэгу """
    # форма задавания вопроса
    question_helper = create_question_form_helper(request)
    question_form = question_helper.question_form
    question = question_helper.question

    # все вопросы с нужным тэгом
    questions = Question.objects.all()
    questions = questions.filter(related_tags__name=tag_name)

    if request.method == 'POST':
        if question_form.is_bound and question:
            # создан новый вопрос на странице
            # с результатами поиска по тэгу
            return redirect('question', str(question))

    return render(request, 'tag.html',
                  {'questions': questions,
                   'form': question_form,
                   'tags': question_helper.tags}
                  )


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

