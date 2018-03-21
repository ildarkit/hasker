from collections import namedtuple

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from .models import Tag, Answer, Question
from .forms import AnswerCreateForm, QuestionCreateForm


def voting(request, question):
    """
     Голосование за вопросы и ответы,
     выбор правильного ответа автором вопроса
    """
    votes = {'up_vote': request.GET.get('up_vote', None),
             'down_vote': request.GET.get('down_vote', None),
             'up_answer_id': request.GET.get('up_answer_id', None),
             'down_answer_id': request.GET.get('down_answer_id', None),
             'correct_answer_id': request.GET.get('correct_answer_id', None)
             }

    user = request.user
    for key in votes:
        if votes[key]:
            if 'vote' in key:
                user.question_voting(question, key)
            else:
                answer = Answer.objects.get(pk=votes[key])
                if 'correct' in key:
                    user.set_correct_answer(question, answer)
                elif 'answer' in key:
                    user.answer_voting(question, answer, key)
            break


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


def get_question(request, header):
    question = None
    if request.method == 'GET':
        pk = request.GET.get('pk')  # переход по ссылке
        new_question_id = request.session.pop('new_question_id', None)  # был создан новый вопрос
        new_question_id = pk or new_question_id
        updated_question_id = request.session.pop(  # после голосования или добавления ответа
            'updated_question_id', None
        )
        if new_question_id:
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
                pass
            else:
                request.session['question_id'] = str(question.pk)

    return question


def render_404_page(request):
    if request.POST:
        question_form = QuestionCreateForm(request.POST)
        if question_form.is_valid():
            question = question_form.set_question(request)
            if question:
                request.session['new_question_id'] = question.pk
                return redirect('question', str(question))
    else:
        question_form = QuestionCreateForm()
    return render(request, '404.html', status=404,
                  context={'form': question_form,
                           'tags': Tag.objects.all(),
                           'trends': Question.objects.all()[:20]}
                  )
