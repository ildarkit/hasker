from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Question
from .forms import AnswerCreateForm

from .helpers import voting, get_question
from .helpers import create_answer_form_helper
from .helpers import render_or_redirect_question, render_404_page

from website.helpers import pagination


def index(request):
    if request.path != '/':
        return render_404_page(request)
    else:
        return redirect('ask')


def question_list_view(request):
    """Главная страница со списком вопросов"""

    questions = pagination(request, Question.objects.all(),
                           20, 'questions_page', sorting=True)

    return render_or_redirect_question(request, 'qa/list.html',
                                       {'questions': questions})


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
    if request.user.is_authenticated:
        answer_form = AnswerCreateForm()
    else:
        answer_form = ()

    question = get_question(request, header)
    if not question:
        return render_404_page(request)

    # На случай, если не прошла валидация формы вопроса,
    # может потребоваться восстановить вопрос, на странице которого
    # создавался новый вопрос.
    # Сохраняется он в контексте при вызове render внутри render_or_redirect_question
    if request.method == 'POST':
        question = Question.objects.get(pk=request.session['question_id'])

    answers = pagination(request, question.answers.all(), 30, 'answers_page')

    return render_or_redirect_question(
        request,
        'qa/question.html',
        {'question': question,
         'answer_form': answer_form,
         'answers': answers}
    )


@login_required
def vote_view(request):
    question_id = request.GET.get('question_id')
    question = Question.objects.get(pk=question_id)

    voting(request, question)

    request.session['updated_question_id'] = str(question.pk)
    return redirect('question', str(question))
