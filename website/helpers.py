from collections import namedtuple

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .qa.models import Tag
from .qa.models import Answer
from .qa.forms import AnswerCreateForm
from .qa.forms import QuestionCreateForm


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


def pagination(request, model_objects, per_page_count, saved_page_name='', sorting=False):
    # Пагинация объектов модели на странице
    if sorting:
        sorting = request.GET.get('sorting', None) or request.session.get('sorting', None)
        if sorting == 'date':
            sort = '-pub_date'
        else:
            sort = 'rating'
        request.session['sorting'] = sorting
        model_objects = model_objects.order_by(sort)

    page = request.GET.get('page', None) or request.session.get(saved_page_name, None)
    if page:
        request.session[saved_page_name] = page
    else:
        page = 1
    paginator = Paginator(model_objects, per_page_count)
    try:
        model_objects = paginator.page(page)
    except PageNotAnInteger:
        model_objects = paginator.page(1)
    except EmptyPage:
        model_objects = paginator.page(paginator.num_pages)
    return model_objects


def create_question_form_helper(request):
    """ Вспомогательная функция создания формы вопроса"""
    if request.POST:
        question_form = QuestionCreateForm(request.POST)
    else:
        question_form = QuestionCreateForm()
    question = question_form.set_question(request)
    tags = Tag.objects.all()
    QuestionHelper = namedtuple('QuestionHelper', ('question_form', 'question', 'tags'))
    return QuestionHelper(question_form, question, tags)


def create_answer_form_helper(request):
    """ Вспомогательная функция создания формы ответа"""
    if request.POST:
        answer_form = AnswerCreateForm(request.POST)
    else:
        answer_form = AnswerCreateForm()
    answer = answer_form.set_answer(request)
    AnswerHelper = namedtuple('AnswerHelper', ('answer_form', 'answer'))
    return AnswerHelper(answer_form, answer)


def render_404_page(request):
    question_helper = create_question_form_helper(request)
    if request.method == 'POST':
        return redirect('question', str(question_helper.question))
    return render(request, '404.html',
                  context={'form': question_helper.question_form,
                           'tags': question_helper.tags})