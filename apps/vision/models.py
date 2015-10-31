#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#

from core.models import BaseModel
from django.db import models
from utils import eggs, logs
from core.managers import BaseManager

class RoadManager(BaseManager):
    
    def all_real_roads(self):
        '''返回所有真路名'''
        return self.filter(is_real=True, is_valid=True)
    
    def all_kana_roads(self):
        '''返回所有假路名'''
        return self.filter(is_real=False, is_valid=True) 
    
class TrialParamManager(BaseManager):
    
    def latest_coming(self):
        '''获取最新一条可用的参数数据'''
        return self.filter(is_coming=True).order_by('-created_time')[0]
    
    def set_not_coming(self):
        '''设置即将使用的参数记录为False'''
        TrialParam.objects.filter(is_coming=True).update(is_coming=False)    

class RoadModel(BaseModel):
    name = models.CharField(u'路名', max_length=40, null=True, blank=True, default='') #作为医生时要显示真实姓名
    is_real = models.BooleanField(u'是真路名', default=False)
    
    is_valid = models.BooleanField(u'有效', default=True)
    

    objects = RoadManager()
    
    class Meta:
        db_table = 'vision_road'
        verbose_name = u'路名'
        verbose_name_plural = u'路名'

    def __unicode__(self):
        return u'%s' % self.name
    

    
# 路牌类型
BOARD_CATE = (
    ('S', u'单路牌'),
    ('M', u'多路牌'),
)    

DEMO_SCHEME_CHOICES = ( #试验模式
    ('S', u'静态'),
    ('D', u'动态'),
)

MOVE_TYPE_CHOICES = (  #运动模式
    ('C', u'圆周'),
    ('S', u'平滑'),
    ('M', u'混合'),
    ('O', u'MOT'),
)
    
class TrialParam(BaseModel):
    '''试验数据模型: 初始参数设置记录'''
    
    board_type = models.CharField(u'路牌类型', max_length=1, choices=BOARD_CATE, default='S')#默认单路牌
    demo_scheme = models.CharField(u'试验模式', max_length=1, choices=DEMO_SCHEME_CHOICES, default='S')#默认静态试验
    move_type = models.CharField(u'运动模式', max_length=1, choices=MOVE_TYPE_CHOICES, null=True, blank=True)#运动模式, 仅当试验模式为动态时有效
    board_size = models.CharField(u'路牌尺寸', max_length=20, default='280,200') #路牌尺寸 
    road_size = models.IntegerField(u'路名大小', default=15) 
    road_num = models.IntegerField(u'路名条数', default=3)
    road_marks = models.CharField(u'路名位置标记', max_length=30)  #如: 'A','B','C'|'A', 分为两部分, 前面为路名位置,以','分隔, 最后以|分隔目标路名 
    eccent = models.IntegerField(u'离心率', null=True, blank=True) 
    init_angle = models.IntegerField(u'初始角度', null=True, blank=True, default=0)

    trialed_count = models.IntegerField(u'执行次数', null=True, blank=True, default=0) #数据被执行次数
    
    #下次试验将被使用, 则其他参数数据将失效. 每次仅有一条数据可用
    is_coming = models.BooleanField(u'是否可用', default=True)
    desc = models.CharField(u'描述', max_length=40, null=True, blank=True, default='')

    objects = TrialParamManager()
    
    class Meta:
        verbose_name = u'试验参数'
        verbose_name_plural = u'试验参数'

    def __unicode__(self):
        res = ''
        if self.board_type == 'S':
            res += u'单路'
        else:
            res += u'多路'
        if self.demo_scheme == 'S':
            res += u'静态'
        else:
            res += u'动态'                
                
        return u'%s %s' % (self.id, res)    
        
    def get_board_size(self):
        size = self.board_size.split(',')
        return size[0], size[1]
        
    def get_road_seats(self):
        '''将路名位置字符串分解后返回, 如'A,B,D|B'分解后返回 ['A', 'B', 'D'], 'B'   
        '''
        roads_str, target_road = self.road_marks.split('|')
        return roads_str.split(','), target_road
        
    def be_executed(self):
        '''被执行一次, 执行次数加1'''
        self.trialed_count += 1
        self.save()

