from collections import namedtuple

from django.db import transaction
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from .models import Tag, Answer, Question
from .forms import AnswerCreateForm, QuestionCreateForm

from website.helpers import pagination


def voting(request, question, vote_type, answer_slug):
    """
     Голосование за вопросы и ответы,
     выбор правильного ответа автором вопроса
    """

    user = request.user

    if answer_slug:
        answer_pk = answer_slug.split('-')[1]
        answer = Answer.objects.get(pk=answer_pk)
        try:
            vote_type = int(vote_type)
        except ValueError:
            question.set_correct_answer(answer)
        else:
            answer.vote(user, vote_type)
    else:
        question.vote(user, int(vote_type))


def create_question_form_helper(request):
    """ Вспомогательная функция создания формы вопроса"""
    question = None
    if request.POST:
        question_form = QuestionCreateForm(request.POST)
        if len(question_form.fields & request.POST.keys()) != len(question_form.fields):
            # запрос не для этой формы, т.к. нет совпадения по полям
            # восстанавливаем пустую форму
            question_form = QuestionCreateForm()
    else:
        question_form = QuestionCreateForm()
    if question_form:
        with transaction.atomic():
            question = question_form.set_question(request)
    if question:
        request.session['new_question_id'] = question.pk
    tags = Tag.objects.all()
    QuestionHelper = namedtuple('QuestionHelper', ('question_form', 'question', 'tags'))
    return QuestionHelper(question_form, question, tags)


def render_or_redirect_question(request, template, context=None):
    """
    Переход на страницу вопроса, в случае удачной валидации формы вопроса.
    Если же это не так, то рендерится текущая страница.
    """

    context = context or {}
    question_helper = None
    question_form = ()
    tags = ()

    if request.method == 'GET' or request.user.is_authenticated:
        question_helper = create_question_form_helper(request)

    if question_helper:
        question_form = question_helper.question_form
        question = question_helper.question
        tags = question_helper.tags

    if question_form and question_form.is_bound and question:
        # переход на страницу вопроса
        return redirect('question', str(question))

    context.update({'form': question_form, 'tags': tags,
                    'trends': Question.objects.all()[:20]})

    return render(request, template, context=context)


def create_answer_form_helper(request):
    """ Вспомогательная функция создания формы ответа"""
    if request.POST:
        answer_form = AnswerCreateForm(request.POST)
    else:
        answer_form = AnswerCreateForm()
    answer = answer_form.set_answer(request)
    AnswerHelper = namedtuple('AnswerHelper', ('answer_form', 'answer'))
    return AnswerHelper(answer_form, answer)


def get_question(func):
    def wrapper(request, slug):
        question = None
        answers = None
        if request.method == 'GET':
            try:
                question = Question.objects.get(slug=slug)
            except ObjectDoesNotExist:
                pass
            else:
                request.session['question_id'] = str(question.pk)

        elif request.method == 'POST':
            # На случай, если форма создания вопроса не прошла валидацию,
            # может потребоваться восстановить вопрос, на странице которого
            # создавался этот новый вопрос.
            # Сохраняется он в контексте при вызове render внутри render_or_redirect_question
            question = Question.objects.get(pk=request.session['question_id'])

        if question:
            answers = pagination(request, question.answers.all(), 30, 'answers_page')
            error = None
        else:
            error = True

        return func(request, slug, error, context={'question': question, 'answers': answers})
    return wrapper

