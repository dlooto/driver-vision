#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#
from utils import http, logs, eggs
from config import *
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from vision.models import TrialParam
from core.views import CustomAPIView


admin_view = admin.site.admin_view


class ParamsIndex(TemplateView):
    '''进入试验参数设置界面'''
    
    template_name = 'admin/index.html'

    @method_decorator(admin_view)
    def dispatch(self, request, *args, **kwargs):
        return super(ParamsIndex, self).dispatch(request, *args, **kwargs)

class ParamsSetView(CustomAPIView):
    '''基础类为单路牌情况. '''
    
    def check_roads_set(self, road_marks):
        ''' 单路牌情况
        @param road_marks: 路名设置, 如 A,B,C,D,A|A,B,D
        '''
        roads_str, targets_str = road_marks.split('|')
        mark_list = roads_str.split(',')
        target_list = targets_str.split(',')
        
        if not set(target_list).issubset(set(mark_list)): #若不是子集关系
            logs.inf(__name__, eggs.lineno(), target_list, mark_list)
            return False, u'目标项 %s 不在设置的路名里 %s' % (target_list, mark_list)
        
        return True, ''
    
#     def get_roads_num(self, road_marks):
#         return '%s' % len(road_marks.split('|')[0].split(','))
    
    def extend_params(self, req, params):
        pass
    
    def post(self, req):
        '''创建新的试验. 管理者参数设置完毕, 并点击确认后请求该方法
        ''' 
        
        board_type = req.POST.get('board_type')     #路牌类型: 单路牌或多路牌(S/M)
        demo_scheme = req.POST.get('demo_scheme')   #试验模式: 静态/动态(S/D)
        step_scheme = req.POST.get('step_scheme')   #试验模式: 静态/动态(S/D)
        move_type = req.POST.get('move_type')       #动态模式: 圆周/平滑/混合/MOT(C/S/M/O)
        
        board_size = req.POST.get('board_size')     #路牌大小: 280,200/420,300
        road_size = req.POST.get('road_size')       #路名尺寸
        road_marks = req.POST.get('road_marks')     #路名设置: 'A,B,C,D,A|A,B,D::B,D,E,A|D,E'
        
        eccent = req.POST.get('eccent')#路牌中心距
        init_angle = req.POST.get('init_angle')#初始角度
        
        correct, msg = self.check_roads_set(road_marks)
        if not correct:
            return http.failed(msg)
        
        try:
            params = {
                "board_type":   board_type, 
                "demo_scheme":  demo_scheme,
                "step_scheme":  step_scheme, 
                "move_type":    move_type, 
                
                "board_size":   board_size, 
                "road_size":    int(road_size),
                "road_marks":   road_marks, 
                
                "eccent":       eccent,
                "init_angle":   init_angle,
            }
        
            self.extend_params(req, params)
        
            TrialParam.objects.set_not_coming()
            trial_param = TrialParam(**params)
            trial_param.save()
        except Exception, e:
            logs.error(e)
            return http.failed(u'参数设置失败')
        
        return http.ok()        

class MultiBoardParamsSetView(ParamsSetView):
    
    def check_roads_set(self, road_marks):
        '''多路牌情况
        @param road_marks: 路名设置, 如 A,B,C,D,A|A,B,D::B,D,E,A|D,E
        '''
        roads_str_list = road_marks.split('::')
        for roads_str in roads_str_list: #for every 'B,D,E,A|D,E'
            road_str, target_str = roads_str.split('|')
            road_list = road_str.split(',')
            target_list = target_str.split(',')
            if not set(target_list).issubset(set(road_list)): #若不是子集关系
                logs.inf(__name__, eggs.lineno(), target_list, road_list)
                return False, u'目标项 %s 不在设置的路名里 %s' % (target_list, road_list)
        
        return True, ''
    
#     def get_roads_num(self, road_marks):
#         '''@param road_marks:  like  A,B,C,D,A|A,B,D::B,D,E,A|D,E
#         '''
#         nums = []
#         roads_str_list = road_marks.split('::')
#         for roads_str in roads_str_list:
#             nums.append(len(roads_str.split('|')[0].split(',')))
#         return ','.join(nums)
    
    def extend_params(self, req, params):
        board_scale = req.POST.get('board_scale')   #多路牌缩放比例       
        board_range = req.POST.get('board_range')   #多路牌排列
        board_space = req.POST.get('board_space')   #多路牌间距
        
        extras = {
            "board_scale":  float(board_scale),
            "board_range":  board_range,
            "board_space":  float(board_space),
        }
        params.update(extras)


    
    
        