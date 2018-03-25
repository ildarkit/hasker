from django.db import transaction
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .models import Question, Tag
from .forms import AnswerCreateForm, QuestionCreateForm

from .helpers import voting, get_question
from .helpers import create_answer_form_helper
from .helpers import render_or_redirect_question

from website.helpers import pagination


def index(request):
    return redirect('ask')


def question_list_view(request):
    """Главная страница со списком вопросов"""

    questions = pagination(request, Question.objects.all(),
                           20, 'questions_page', sorting=True)

    return render_or_redirect_question(request, 'qa/list.html',
                                       {'questions': questions})


@transaction.atomic
def answer_view(request, slug):
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
        question = Question.objects.get(slug=slug)
        answer.question = question
        answer.save()
        request.session['new_answer_id'] = answer.pk
        return redirect('question', slug)
    elif request.method == 'GET':
        return page_404_view(request)


@get_question
def question_view(request, slug, **kwargs):
    """ Страница вопроса со списком ответов """
    if kwargs.get('error'):
        # не удалось получить вопрос
        return page_404_view(request)
    if request.user.is_authenticated:
        answer_form = AnswerCreateForm()
    else:
        answer_form = ()

    ctx = {'answer_form': answer_form}
    if kwargs.get('context'):
        ctx.update(kwargs['context'])

    return render_or_redirect_question(request, 'qa/question.html',
                                       context=ctx)


@login_required()
def vote_view(request, slug, vote_type, answer_slug=None):
    """ Голосование за вопрос, ответы и выбор правильного ответа"""
    question = Question.objects.get(slug=slug)

    voting(request, question, vote_type, answer_slug)

    return redirect('question', slug)


@transaction.atomic
def page_404_view(request):
    if request.POST:
        question_form = QuestionCreateForm(request.POST)
        if question_form.is_valid():
            question = question_form.set_question(request)
            if question:
                return redirect('question', str(question))
    else:
        question_form = QuestionCreateForm()
    return render(request, '404.html', status=404,
                  context={'form': question_form,
                           'tags': Tag.objects.all(),
                           'trends': Question.objects.all()[:20]}
                  )
