#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#

from core.models import BaseModel
from django.db import models
from utils import eggs, logs
from config import *
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
        '''获取最新一条可用的初始参数'''
        return self.filter(is_coming=True).order_by('-created_time')[0]
    
    def set_not_coming(self):
        '''设置即将使用的参数记录为False'''
        TrialParam.objects.filter(is_coming=True).update(is_coming=False)    

class RoadModel(BaseModel):
    '''作为路名字典'''
    name = models.CharField(u'路名', max_length=40, null=True, blank=True, default='')
    is_real = models.BooleanField(u'是真路名', default=False)
    
    is_valid = models.BooleanField(u'有效', default=True)
    

    objects = RoadManager()
    
    class Meta:
        db_table = 'vision_road'
        verbose_name = u'Road'
        verbose_name_plural = u'Roads'

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

BOARD_RANGE_CHOICES = ( #路牌排列选择
    ('H', u'横'),
    ('V', u'纵'),
)

STEP_SCHEME_CHOICES = (  #阶梯类型
    ('R', u'关键间距'),
    ('N', u'数量阈值'),
    ('S', u'尺寸阈值'),
    ('V', u'动态敏感度'),                           
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
    step_scheme = models.CharField(u'阶梯类型', max_length=1, choices=STEP_SCHEME_CHOICES, default='R')#默认求关键间距
    move_type = models.CharField(u'运动模式', max_length=1, choices=MOVE_TYPE_CHOICES, null=True, blank=True)#运动模式, 仅当试验模式为动态时有效
    
    board_size = models.CharField(u'路牌尺寸', max_length=20, default='280,200') #所设为最大路牌尺寸, 其他路牌按比例(board_scale)依次缩放 
    road_size = models.IntegerField(u'路名尺寸', default=15) #所设为最大路名尺寸, 其他路牌上的路名按比例(board_scale)依次缩放
    
    board_scale = models.FloatField(u'路牌缩放比例', default=1.0, null=True, blank=True) #多路牌使用  
    board_range = models.CharField(u'路牌排列', max_length=1, choices=BOARD_RANGE_CHOICES, default='H', null=True, blank=True)#多路牌使用
    board_space = models.FloatField(u'路牌间距', null=True, blank=True) #多路牌使用
    
    #多路牌时多个数量以逗号间隔, 形如: 3,5,7
    #road_num = models.CharField(u'路名数量', max_length=10, default='3')   
    
    #如: 'A,B,C|A,C', 以|分隔为两部分, 前面为路名位置,最后遍历的目标路名. 多路牌时以::号分隔各路牌上的路名设置       
    road_marks = models.CharField(u'路名位置标记|目标标记', max_length=100)  
    
    # 路牌中心距, 即路牌中心离注视点的距离. 最多3个值, 各值间以,分隔
    eccent = models.CharField(u'路牌中心距离', max_length=40, null=True, blank=True)
    
    #路牌中心-注视点连线与水平线的夹角. 顺时针方向旋转为角度增大. 最多3个值, 各值间以,分隔
    init_angle = models.CharField(u'初始角度', max_length=40, null=True, blank=True)

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
                
        return u'%s-%s' % (self.id, res)    
        
    def is_single(self):
        '''是否单路牌类型'''
        return True if self.board_type == 'S' else False
                    
    def is_static(self):
        '''是否静态模式'''
        return True if self.demo_scheme == 'S' else False                    
        
    def get_board_size(self):
        size = self.board_size.split(',')
        return int(size[0]), int(size[1])
        
    def get_road_seats(self):# TODO...
        '''将路名位置字符串分解后返回, 如'A,B,D|B,D'分解后返回 ['A', 'B', 'D'], ['B', 'D'] 
        第1个列表为所有路名位置, 第2个列表为可选的目标项位置  
        '''
        roads_str, targets_str = self.road_marks.split('|')
        return roads_str.split(','), targets_str.split(',')
    
    def be_executed(self):
        '''被执行一次, 执行次数加1'''
        self.trialed_count += 1
        self.save()
        
    def get_eccents(self):
        '''返回路牌中心距列表(浮点值列表)''' 
        return [float(e) for e in self.eccent.split(',')]
    
    def get_angles(self):
        '''返回初始角度值列表(浮点值列表)''' 
        return [float(a) for a in self.init_angle.split(',')]
               
        
        
class Demo(BaseModel):
    '''一次完整试验记录'''
    
    param = models.ForeignKey(TrialParam, verbose_name=u'初始参数', null=True, blank=True) #所使用的初始参数设置
    correct_rate = models.FloatField(u'试验正确率', default=0)
    time_cost = models.FloatField(u'耗费时间(秒)', default=0.0) #秒数
    is_break = models.BooleanField(u'是否被中断', default=False) #实验被中断时置为True
    desc = models.CharField(u'描述', max_length=40, null=True, blank=True, default='')
    
    class Meta:
        db_table = 'vision_demo'
        verbose_name = u'Demo'
        verbose_name_plural = u'Demos'

    def __unicode__(self):
        return u'%s' % self.id
    
# 阶梯变化类型
STEP_TYPE_CHOICES = {
    ('N', u'数量(N)'),
    ('S', u'尺寸(S)'),
    ('R', u'间距(R)'),
    ('V', u'速度(V)'),                             
}    
    
class Block(BaseModel):
    '''连续的阶梯变化为一个Block, 一般40次trial属于一个Block'''
    
    demo = models.ForeignKey(Demo, verbose_name=u'所属Demo')
    tseat = models.CharField(u'目标位置(D)', max_length=1)      #如A/B/C/...
    ee = models.FloatField(u'离心率(E)', null=True, blank=True)   #目标项与注视点距离               
    angle = models.IntegerField(u'角度(@)') #目标项与注视点连线夹角                   
    
    cate = models.CharField(u'阶梯类别', max_length=1, choices=STEP_TYPE_CHOICES) #阶梯变化类型
                         
    
    ## 以下参数根据求不同的阈值时不同时存在. 如求数量阈值时, N的阶梯变化值将记录在Trial模型中, 
    # 而此时Block中N字段将为空
    N = models.SmallIntegerField(u'干扰项数量(N)', null=True, blank=True, default=1)
    S = models.FloatField(u'路名尺寸(S)', null=True, blank=True)
    R = models.CharField(u'目干间距(R)', max_length=40, null=True, blank=True)    #目标与干扰项间距, 多个间距以逗号分隔, 如:r1,r2,r3
    V = models.FloatField(u'目标项速度(V)', null=True, blank=True, default=0.0)  
    
    class Meta:
        db_table = 'vision_block'
        verbose_name = u'Block'
        verbose_name_plural = u'Blocks'

    def __unicode__(self):
        return u'%s' % self.id
    
class Trial(BaseModel):
    '''一次刺激显示中的数据记录'''
    
    block = models.ForeignKey(Block, verbose_name=u'所属Block')
    cate = models.CharField(u'阶梯类型', max_length=1, choices=STEP_TYPE_CHOICES) #阶梯变化类型, 由此决定steps_value记录的值类型
    
    resp_cost = models.FloatField(u'响应时间', default=show_interval) #秒数
    is_correct = models.BooleanField(u'判断正确', default=False) #按键判断是否正确
    steps_value = models.CharField(u'阶梯值', max_length=50, )  #阶梯法记录值. 当间距阶梯变化时, 该值形如: r1,r2,r3(3个干扰项与目标项间距的以逗号分隔的字符串); 其他情况为单值
    target_road = models.CharField(u'目标路名', max_length=40, null=True, blank=True, default='')   #由此可知道用户按键情况
    #start_time = models.DateTimeField(u'开始时间', )
    
    class Meta:
        db_table = 'vision_trial'
        verbose_name = u'Trial'
        verbose_name_plural = u'Trials'

    def __unicode__(self):
        return u'%s, %s, %s, %s, %s, %s' % (
                         self.block,                   
                         self.cate, 
                         self.resp_cost, 
                         self.is_correct,
                         self.steps_value,
                         self.target_road
                         )
    
class BoardLog(BaseModel):
    '''一次刺激显示中的路牌数据
    @todo: ...
    '''
    
    trial = models.ForeignKey(Trial, verbose_name=u'所属刺激显示')
    #pos, width, height, road_marks, ...
    
    class Meta:
        db_table = 'vision_boardlog'
        verbose_name = u'boardlog'
        verbose_name_plural = u'boardlog'

    def __unicode__(self):
        return self.id        
    
        
        
        
        
        
        
        
        
        
        
        
        