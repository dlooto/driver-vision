#coding=utf-8
#
# Created on Apr 21, 2014, by Junn
# 
#

from django.conf.urls import patterns, url

from auth import views

urlpatterns = patterns(
    '',
    
    url(r'^/login$',         views.LoginAction.as_view(),   name='auth_login'),
    url(r'^/logout$',        views.logout,                  name='auth_logout'),
    
)
