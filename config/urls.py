"""hasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include


from website import profiles


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'search/$', views.search, name='search'),
    url(r'ask/', views.question_list_view, name='ask'),
    url(r'question/(?P<header>[\w-]+)/$', views.question_view, name='question'),
    url(r'vote/$', views.vote_view, name='vote'),
    url(r'answer/$', views.answer_view, name='answer'),
    url(r'tag/(?P<tag_name>[\w]+)/$', views.tag_view, name='tag_search'),
    url(r'login/$', profiles.views.login_view, name='login'),
    url(r'logout/$', profiles.views.logout_view, name='logout'),
    url(r'signup/$', profiles.views.signup_view, name='signup'),
    url(r'settings/$', profiles.views.settings_view, name='settings'),
    url(r'$', views.index, name='index'),
    ]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns