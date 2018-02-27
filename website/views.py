from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory
from django.db.models import Prefetch
from django.contrib.auth import authenticate, login, logout

from .models import Question
from .models import Answer
from .models import HaskerUser
from .forms import QuestionCreateForm
from .forms import UserCreateForm


class ListQuestionsView(TemplateView):

    template_name = 'list.html'

    def get_context_data(self, **kwargs):
        context = super(ListQuestionsView, self).get_context_data(**kwargs)
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
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = None
        form = self.get_form()
        if form.is_valid():
            model_instance = form.save()
            request.session['question_id'] = str(model_instance.pk)
            return redirect('question', kwargs={'header': model_instance})
        else:
            return self.form_invalid(form)


def search(request):
    pass


def index(request):
    return redirect('ask')


def question(request, header):
    question_id = request.session.pop('question_id', None)
    if question_id:
        # question = get_object_or_404(Question, pk=int(question_id))
        question_query = Question.objects.filter(pk=question_id)
    else:
        header = header.replace('-', ' ')
        question_query = Question.objects.filser(header=header)
    if request.method == 'GET':
        return render(request, 'question.html',
                      context={'questions': question_query})


def tag(request):
    pass


def logout_view(request):
    logout(request)
    return redirect('ask')


class SignUpView(CreateView):
    model = HaskerUser
    form_class = UserCreateForm
    template_name = 'signup.html'

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            model_instance = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('ask')
        else:
            return self.form_invalid(form)


def settings(request):
    pass

