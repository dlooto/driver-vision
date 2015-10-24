#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#

from django.conf.urls import patterns, url

from vision import views
import settings

urlpatterns = patterns(
    '',
    url(r'^/new_demo$',         views.new_demo),
    url(r'^/start_demo$',       views.start_demo),
    
)