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
def set_params(req):
    '''创建新的试验. 管理者参数设置完毕, 并点击确认后请求该方法
    ''' 
    
    board_type = req.POST.get('board_type')
    demo_scheme = req.POST.get('demo_scheme')
    dynamic_type = req.POST.get('dynamic_type')
    board_size = req.POST.get('board_size')
    road_size = req.POST.get('road_size')
    road_num = req.POST.get('road_num')
    road_marks = req.POST.get('road_marks')
    target_road = req.POST.get('target_road')
    
    eccent = req.POST.get('eccent')
    init_angle = req.POST.get('init_angle')
    
    return http.ok({"board_type":   board_type, 
                    "demo_scheme":  demo_scheme, 
                    "dynamic_type": dynamic_type, 
                    "road_num":     road_num,
                    "road_marks":   road_marks,
                    "target_road":  target_road,
                    "eccent":       eccent,
                    "init_angle":   init_angle,
                    "road_size":    road_size,
                    "board_size":   board_size, 
        })
    
class ParamsSet(TemplateView):
    '''进入试验参数设置界面'''
    
    template_name = 'admin/params_set.html'

    @method_decorator(admin_view)
    def dispatch(self, request, *args, **kwargs):
        return super(ParamsSet, self).dispatch(request, *args, **kwargs)
        