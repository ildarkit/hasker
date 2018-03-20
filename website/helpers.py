from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def pagination(request, model_objects, per_page_count, saved_page_name='', sorting=False):
    # Пагинация объектов модели на странице
    if sorting:
        sorting_by = request.GET.get('sorting', None) or request.session.get('sorting', None)
        if sorting_by == 'date' or sorting_by is None:
            sort = '-pub_date'
        else:
            sort = '-rating'
        if sorting_by:
            request.session['sorting'] = sorting_by
        model_objects = model_objects.order_by(sort)

    page = request.GET.get('page', None) or request.session.get(saved_page_name, None)
    if page and saved_page_name:
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
