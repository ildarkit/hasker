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

import website.profiles.views as profile_views
import website.qa.views as question_views
import website.search.views as search_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'avatars/', profile_views.get_user_icon_view, name='get_icon'),
    url(r'search/$', search_views.search_view, name='search'),
    url(r'ask/', question_views.question_list_view, name='ask'),
    url(r'question/(?P<header>[\w-]+)/$', question_views.question_view, name='question'),
    url(r'vote/$', question_views.vote_view, name='vote'),
    url(r'answer/$', question_views.answer_view, name='answer'),
    url(r'tag/(?P<tag_name>[\w]+)/$', search_views.tag_search_view, name='tag_search'),
    url(r'login/$', profile_views.login_view, name='login'),
    url(r'logout/$', profile_views.logout_view, name='logout'),
    url(r'signup/$', profile_views.signup_view, name='signup'),
    url(r'settings/$', profile_views.settings_view, name='settings'),
    url(r'$', question_views.index, name='index'),
    ]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns