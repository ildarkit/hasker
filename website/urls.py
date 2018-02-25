from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'search/', views.search, name='search'),
    url(r'ask/', views.ListQuestionsView.as_view(), name='ask'),
    url(r'question/<header>/', views.question, name='question'),
    url(r'tag/', views.tag, name='tag'),
    url(r'login/', views.login, name='login'),
    url(r'signup/', views.signup, name='signup'),
    url(r'setings/', views.settings, name='settings'),
    url(r'$', views.index, name='index'),
]