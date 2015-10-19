#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on Mar 21, 2014, by Junn
# 
#
from django.conf.urls import patterns, url

from users import views
import settings

urlpatterns = patterns(
    '',
    url(r'^$',                  views.UsersAction.as_view()),
    url(r'^/(\d+)$',            views.UserView.as_view()),
    
)

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^/current$', views.info),)  
