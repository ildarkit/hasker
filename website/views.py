from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Question


class ListPage(TemplateView):

    template_name = 'list.html'

    def get_context_data(self, **kwargs):
        context = super(ListPage, self).get_context_data(**kwargs)
        question_list = Question.objects.all()
        paginator = Paginator(question_list, 20)
        page = self.request.GET.get('page')
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            questions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            questions = paginator.page(paginator.num_pages)
        context['questions'] = questions
        return context


def search(request):
    pass


def index(request):
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

