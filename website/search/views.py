from django.db.models import Q
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response

from website.qa.models import Question
from website.helpers import create_question_form_helper


def tag_search_view(request, tag_name):
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

    return render(request, 'search/tag.html',
                  {'questions': questions,
                   'form': question_form,
                   'tags': question_helper.tags}
                  )


def search_view(request):
    query = request.GET.get('q')
    questions = Question.objects.filter(
        Q(header__contains=query) | Q(text__contains=query)
    )
    return render_to_response('search/search.html', {"questions": questions, })
