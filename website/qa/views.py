from django.shortcuts import render
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from .models import Question
from .models import Answer
from .forms import AnswerCreateForm

from .helpers import voting
from .helpers import create_answer_form_helper
from .helpers import create_question_form_helper

from website.helpers import pagination
from website.helpers import render_404_page


def index(request):
    if request.path != '/':
        return render_404_page(request)
    else:
        return redirect('ask')


def question_list_view(request):
    """Главная страница со списком вопросов"""
    question_helper = create_question_form_helper(request)
    question = question_helper.question
    if request.method == 'POST' and question:
        return redirect('question', str(question))

    questions = pagination(request, Question.objects.all(),
                           4, 'questions_page', sorting=True)

    return render(request, 'qa/list.html',
                  context={'questions': questions,
                           'form': question_helper.question_form,
                           'tags': question_helper.tags})


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

        answers = pagination(request, question.answers.all(),
                             4, 'answers_page')

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
                answers = pagination(request, question.answers.all(), 4, 'answers_page')

    return render(request, 'qa/question.html',
                  context={'question': question,
                           'form': question_form,
                           'answer_form': answer_form,
                           'answers': answers,
                           'tags': question_helper.tags})


@login_required
def vote_view(request):
    question_id = request.GET.get('question_id')
    question = Question.objects.get(pk=question_id)

    voting(request, question)

    request.session['updated_question_id'] = str(question.pk)
    return redirect('question', str(question))


