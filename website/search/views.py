from django.db.models import Q
from django.shortcuts import redirect

from website.helpers import pagination
from website.qa.models import Question
from website.qa.helpers import render_or_redirect_question


def tag_search_view(request, tag_name):
    """ Страница с результатами поиска по тэгу """
    tag_name = tag_name.split(' ,-', maxsplit=1)[0]

    # все вопросы с нужным тэгом
    questions = Question.objects.all()
    questions = questions.filter(related_tags__name=tag_name.lower())

    questions = pagination(request, questions, 20)

    return render_or_redirect_question(request, 'search/tag.html',
                                       {'questions': questions})


def search_view(request):
    query = request.GET.get('q').split(' -,', maxsplit=1)[0][:50]
    if query.startswith('tag:'):
        return redirect('tag_search', query.replace('tag:', ''))

    questions = Question.objects.filter(
        Q(header__icontains=query) | Q(text__icontains=query)
    )

    questions = pagination(request, questions, 20)

    return render_or_redirect_question(request, 'search/search.html',
                                       {"questions": questions, })
