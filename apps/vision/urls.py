#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#

from django.conf.urls import patterns, url

from vision import views
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r"^$",                  views.ParamsIndex.as_view(),    name="vision:params_index"),
    url(r'^/set_params',        views.ParamsSetView.as_view(),  name="set_params"),             #单路牌参数设置
    url(r'^/set_multi_params',  views.MultiBoardParamsSetView.as_view(),  name="set_multi_params"), #多路牌参数设置
    
    url(r"^/single_board$", TemplateView.as_view(template_name='admin/single_board_params.html')),  
    url(r"^/multi_board$",  TemplateView.as_view(template_name='admin/multi_board_params.html')),
    
)