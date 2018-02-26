from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'search/', views.search, name='search'),
    url(r'ask/', views.ListQuestionsView.as_view(), name='ask'),
    url(r'question/<header>/', views.question, name='question'),
    url(r'tag/', views.tag, name='tag'),
    url(r'login/', auth_views.login, {'template_name': 'login.html', }, name='login'),
    url(r'logout/', views.logout_view, name='logout'),
    url(r'signup/', views.SignUpView.as_view(), name='signup'),
    url(r'setings/', views.settings, name='settings'),
    url(r'$', views.index, name='index'),
]