#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#
from utils import http, logs
from vision import trials
from config import *
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view

admin_view = admin.site.admin_view

@api_view(['POST'])
def new_demo(req):
    '''创建新的试验. 管理者参数设置完毕, 并点击确认后请求该方法
    ''' 
    
    hello = req.POST.get('nickname')
    print hello
    
    return http.ok({'hello': hello})
    
class ParamsSet(TemplateView):
    '''进入试验参数设置界面'''
    
    template_name = 'admin/params_set.html'

    @method_decorator(admin_view)
    def dispatch(self, request, *args, **kwargs):
        return super(ParamsSet, self).dispatch(request, *args, **kwargs)
        