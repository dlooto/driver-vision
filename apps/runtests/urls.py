#coding=utf-8
#
# Created on May 18, 2014, by Junn
#

from django.conf.urls import patterns, url

from runtests import views
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^/qq_login$',  TemplateView.as_view(template_name='auth/qq_login.html')),

)