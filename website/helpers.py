from django.shortcuts import render
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .qa.helpers import create_question_form_helper


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


def render_404_page(request):
    question_helper = create_question_form_helper(request)
    if request.method == 'POST':
        return redirect('question', str(question_helper.question))
    return render(request, '404.html',
                  context={'form': question_helper.question_form,
                           'tags': question_helper.tags})