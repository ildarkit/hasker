from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Question


def index(request):
    question_list = Question.objects.all()
    paginator = Paginator(question_list, 20)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        question = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        question = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        question = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'questions': question})


def search(request):
    pass


def ask(request):
    pass


def question(request):
    pass


def tag(request):
    pass


def login(request):
    pass


def signup(request):
    pass


def settings(request):
    pass

