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
import traceback


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
    
    def extend_params(self, req, params):
        pass
    
    def post(self, req):
        '''创建新的试验. 管理者参数设置完毕, 并点击确认后请求该方法
        ''' 
        
        board_type = req.POST.get('board_type')     #路牌类型: 单路牌或多路牌(S/M)
        demo_scheme = req.POST.get('demo_scheme')   #试验模式: 静态/动态(S/D)
        step_scheme = req.POST.get('step_scheme')   #试验模式: 静态/动态(S/D)
        move_type = req.POST.get('move_type')       #动态模式: 圆周/平滑/混合(C/S/M) MOT模式已调整为别一维度进行参数设置
        wp_scheme = req.POST.get('wp_scheme')       #注视点运动模式: S-静止, L-直线运动  
        velocity = req.POST.get('velocity')         #速度值: 离散值3个
        
        board_size = req.POST.get('board_size')     #路牌大小: 280,200/420,300
        road_size = req.POST.get('road_size')       #路名尺寸
        road_marks = req.POST.get('road_marks')     #路名设置: 'A,B,C,D,A|A,B,D::B,D,E,A|D,E'
        
        eccent = req.POST.get('eccent')             #路牌中心距
        init_angle = req.POST.get('init_angle')     #初始角度
        
        correct, msg = self.check_roads_set(road_marks)
        if not correct:
            return http.failed(msg)
        
        if demo_scheme == 'S':
            move_type = ''
            velocity = ''
        
        try:
            params = {
                "board_type":   board_type, 
                "demo_scheme":  demo_scheme,
                "step_scheme":  step_scheme, 
                "move_type":    move_type, 
                "wp_scheme":    wp_scheme,
                "velocity":     velocity,
                
                "board_size":   board_size, 
                "road_size":    int(road_size),
                "road_marks":   road_marks, 
                
                "eccent":       eccent,
                "init_angle":   init_angle,
            }
        
            self.extend_params(req, params)
            print '\n', params, '\n'
        
            TrialParam.objects.set_not_coming()
            trial_param = TrialParam(**params)
            trial_param.save()
        except Exception:
            traceback.print_exc()
            return http.failed(u'参数设置失败')
        
        return http.ok()        

class MultiBoardParamsSetView(ParamsSetView):
    
    def check_roads_set(self, road_marks):
        '''多路牌情况
        @param road_marks: 路名设置, 如 A,B,C,D,A|A,B,D::B,D,E,A|D,E
        '''
        if not road_marks:
            return False, 'road_marks NULL'
        roads_str_list = road_marks.split('::')
        i = 0
        for roads_str in roads_str_list: #for every 'B,D,E,A|D,E'
            i += 1
            road_str, target_str = roads_str.split('|')
            road_list = road_str.split(',')
            target_list = target_str.split(',')
            if not set(target_list).issubset(set(road_list)): #若不是子集关系
                logs.err(__name__, eggs.lineno(), '%s not in %s' % (target_list, road_list))
                return False, u'路牌-%s: 目标项 %s 不在设定的路名里 %s' % (i, target_list, road_list)
        
        return True, ''
    
    def extend_params(self, req, params):
        board_scale = req.POST.get('board_scale')   #多路牌缩放比例       
        board_range = req.POST.get('board_range')   #多路牌排列
        board_space = req.POST.get('board_space')   #多路牌间距
        pre_board_num = req.POST.get('pre_board_num') #初始路牌显示数
        
        extras = {
            "board_scale":  float(board_scale),
            "board_range":  board_range,
            "board_space":  float(board_space),
            "pre_board_num":int(pre_board_num),
        }
        params.update(extras)


    
    
        