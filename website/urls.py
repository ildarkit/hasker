from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'search/$', views.search, name='search'),
    url(r'ask/', views.question_list_view, name='ask'),
    url(r'question/(?P<header>\w+)/$', views.question_view, name='question'),
    url(r'tag/', views.tag, name='tag'),
    url(r'login/$', auth_views.login, {'template_name': 'login.html', }, name='login'),
    url(r'logout/$', views.logout_view, name='logout'),
    url(r'signup/$', views.signup_view, name='signup'),
    url(r'settings/$', views.settings_view, name='settings'),
    url(r'$', views.index, name='index'),
]