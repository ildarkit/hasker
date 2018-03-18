from collections import namedtuple

from .models import Tag, Answer
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