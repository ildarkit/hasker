from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Question
from .forms import QuestionCreateForm


class ListPageView(TemplateView):

    template_name = 'list.html'

    def get_context_data(self, **kwargs):
        context = super(ListPageView, self).get_context_data(**kwargs)
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


class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionCreateForm

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = None
        form = self.get_form()
        if form.is_valid():
            model_instance = form.save()
            return redirect('question', kwargs={'pk': model_instance.pk})
        else:
            return self.form_invalid(form)


def search(request):
    pass


def index(request):
    return redirect('ask')


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

