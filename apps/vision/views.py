#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#
from utils import http, logs, eggs
from vision import trials
from config import *
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from vision.models import TrialParam

admin_view = admin.site.admin_view


class ParamsIndex(TemplateView):
    '''进入试验参数设置界面'''
    
    template_name = 'admin/params_set.html'

    @method_decorator(admin_view)
    def dispatch(self, request, *args, **kwargs):
        return super(ParamsIndex, self).dispatch(request, *args, **kwargs)

@api_view(['POST'])
def set_params(req):
    '''创建新的试验. 管理者参数设置完毕, 并点击确认后请求该方法
    ''' 
    
    board_type = req.POST.get('board_type')     #路牌类型: 单路牌或多路牌(S/M)
    demo_scheme = req.POST.get('demo_scheme')   #试验模式: 静态/动态(S/D)
    move_type = req.POST.get('move_type')       #动态模式: 圆周/平滑/混合/MOT(C/S/M/O)
    board_size = req.POST.get('board_size')     #路牌大小: 280,200/420,300
    road_size = req.POST.get('road_size')       #路名尺寸
    road_num = req.POST.get('road_num')         #路名数量
    road_marks = req.POST.get('road_marks')     #路名设置: 'A,B,C,D,A'
    target_seats = req.POST.get('target_seats') #待选目标项: 'A,B,D'
    
    eccent = req.POST.get('eccent')#离心率
    init_angle = req.POST.get('init_angle')#初始角度
    
    # check params
    mark_list = road_marks[0:-1].split(',')
    if int(road_num) > len(mark_list) or int(road_num) < len(mark_list):
        return http.failed(u'路名数量与路名位置数不匹配: 路名数量=%s,  路名位置=%s' % (road_num, mark_list))
    
    target_list = target_seats[0:-1].split(',')
    if not set(target_list).issubset(set(mark_list)): #若不是子集关系
        logs.inf(__name__, eggs.lineno(), target_list, mark_list)
        return http.failed(u'目标项 %s 不在设置的路名里 %s' % (target_list, mark_list))
    
    try:
        params = {"board_type":   board_type, 
                "demo_scheme":  demo_scheme, 
                "move_type":    move_type, 
                "board_size":   board_size, 
                "road_size":    int(road_size),
                "road_num":     int(road_num),
                
                "road_marks":   road_marks[0:-1]+'|'+target_seats[0:-1],  #组装成: 'A,B,C,D|A,D'
                "eccent":       int(eccent),
                "init_angle":   int(init_angle),
        }
    
        TrialParam.objects.set_not_coming()
        trial_param = TrialParam(**params)
        trial_param.save()
    except Exception, e:
        logs.error(e)
        return http.failed(u'参数设置失败')
    
    return http.ok()
    
        