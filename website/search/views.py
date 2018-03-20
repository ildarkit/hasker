from django.db.models import Q
from django.shortcuts import redirect

from website.helpers import pagination
from website.qa.models import Question
from website.qa.helpers import render_or_redirect_question


def tag_search_view(request, tag_name):
    """ Страница с результатами поиска по тэгу """

    # все вопросы с нужным тэгом
    questions = Question.objects.all()
    questions = questions.filter(related_tags__name=tag_name)

    questions = pagination(request, questions, 20)

    return render_or_redirect_question(request, 'search/tag.html',
                                       {'questions': questions})


def search_view(request):
    query = request.GET.get('q')
    if query.startswith('tag:'):
        return redirect('tag_search', query.replace('tag:', ''))

    questions = Question.objects.filter(
        Q(header__contains=query) | Q(text__contains=query)
    )

    questions = pagination(request, questions, 20)

    return render_or_redirect_question(request, 'search/search.html',
                                       {"questions": questions, })
