#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

import random, threading
import maths
from config import *
from vision.models import RoadModel, TrialParam


class WatchPoint(object):
    tk_id = None
    pos = WATCH_POS
    radius = 5
    
    def __init__(self, pos=WATCH_POS, radius=5, fill=watch_color, outline=watch_color):
        self.pos = pos              #坐标点
        self.radius = radius        #圆圈半径
        self.fill = fill            #填充颜色
        self.outline = outline      #边框颜色
    
    def change_params(self, pos=WATCH_POS):
        self.pos = pos
    

cached_real_roads = RoadModel.objects.all_real_roads()
cached_kana_roads = RoadModel.objects.all_kana_roads()

class Board(object):
    '''路牌'''
    
    trial_param = None
    
    pos = BOARD_POS             #中心点坐标, 即路牌位置
    width = 280                 #路牌宽度
    height = 200                #路牌高度
    
    eccent = None               #离心率
    angle = 0                   #路牌初始角度
    road_dict = None            #路名列表
    target_road = None          #目标项
    
    # 辅助变量
    his_seats = []              #已被设定过的目标项位置列表
    
    def __init__(self, pos=BOARD_POS, width=BOARD_SIZE['w'], height=BOARD_SIZE['h']):
        self._load_params()
        
        self.pos = pos
        self.width = width
        self.height = height
        self.watch_point = WatchPoint()
        
        #self.load_road_dict()
    
    def _load_params(self):
        '''从DB加载最新的有效试验参数. '''
        self.trial_param = TrialParam.objects.latest_coming()
        if not self.trial_param:
            raise Exception(u'请先设置有效的试验参数')
        
        self.road_seats, self.target_seats = self.trial_param.get_road_seats()
        self.road_num = self.trial_param.road_num
        
        self.trial_param.be_executed()
    
    def load_road_dict(self, road_num):
        ''' 设置路牌上的所有路名'''
        
        modeled_roads = self.generate_random_roads(road_num)
        target = random.choice(self.target_seats) #初始随机取一个

        self.road_dict = {}
        for mark in self.road_seats:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark] = Road(road_model.name, self.pos_xx(mark), 
                                        is_real=road_model.is_real, 
                                        size=self.trial_param.road_size)
            self.road_dict[mark].is_target = True if mark == target else False
            modeled_roads.remove(road_model)
        self.target_road = self.road_dict.get(target)
        
        self.his_seats.append(target)    #初始化历史目标项位置列表
        
    
    def next_target_seat(self):
        '''切换目标项位置, 从目标'A' --> 'B', 
        每调用一次, his_seats中添加一次已设置过的目标项位置, 如his_seats=['A', 'B']
        '''
        bak_targets = list(set(self.target_seats).difference(set(self.his_seats)))
        target = random.choice(bak_targets)
        self.his_seats.append(target)
        return target
        
    def save_control_params(self, demo_id): 
        '''向DB写入某次试验的控制参数'''   
        pass
    
    def generate_random_roads(self, road_num):
        ''' 根据传入的路名数量, 生成不重复的随机路名列表.
         列表元素类型为Road Model(name, is_real).
        算法规则: 若路名数量为偶数, 则真假路名各一半, 若为奇数, 则假名多1.
        
        '''
        num = road_num / 2
        real_roads = random.sample(cached_real_roads, num)
        if self.trial_param.road_num % 2 == 1: #奇数
            real_roads.extend(random.sample(cached_kana_roads, num+1))
        else: #偶数
            real_roads.extend(random.sample(cached_kana_roads, num))            
                    
        return real_roads
        
    def get_road_num(self):
        return self.trial_param.road_num
    
    def get_eccent(self):
        if not self.eccent: #优先返回当前设定的值
            return self.trial_param.eccent
        return self.eccent
    
    def get_angle(self):
        return self.trial_param.init_angle
    
    def move(self, dx, dy):
        '''路牌移动. dx = p2.x - p1.x, dy = p2.y - p1.y.
        erase()再draw(), 或者canvas.move(board)再canvas.move(roads)
        '''
        pass
    
    def change_params(self, target_seat, eccent, angle, **kwargs):
        '''按指定的算法规则, 控制参数变化'''
        # according target, load road_dict
        self.load_road_dict(target_seat, )
        # 根据目标与干扰项已有坐标(及间距), 循环计算出各干扰项新坐标(根据间距变化及坐标)
        
        self.watch_point.change_params()
        
        #self.pos = self.pos[0], self.pos[1]-5  # 路牌向上移动, for testing... 
        self.load_road_dict() 
        
    
    def save(self):
        # TODO: save board into DB ...
        # 保存一次刺激显示中的路牌状态信息到BoardLog...
        pass
    
    
    # 以路牌中心坐标为参照点, 获取路牌上 A, B, C, D, E, F, G, H各点中心坐标
    def pos_a(self):
        return self.pos[0]-80, self.pos[1]+10
    def pos_b(self):
        return self.pos[0]-80, self.pos[1]+35
    def pos_c(self):
        return self.pos[0]-80, self.pos[1]+60
    def pos_d(self):
        return self.pos[0]+80, self.pos[1]+10
    def pos_e(self):
        return self.pos[0]+80, self.pos[1]+35
    def pos_f(self):
        return self.pos[0]+80, self.pos[1]+60
    def pos_g(self):
        return self.pos[0], self.pos[1]-70
    def pos_h(self):
        return self.pos[0], self.pos[1]-45
    
    def pos_xx(self, mark):
        mt = 'pos_%s' % mark.lower()
        return getattr(self, mt)()
    
#     def draw(self, canvas):
#         '''将路牌绘制在屏幕上, 同是包含注视点'''  
#         
#         #绘制注视点
#         self.watch_point.draw(canvas) 
#         
#         #绘制路牌
#         self.tk_id = canvas.create_rectangle_pro(
#             self.pos[0], self.pos[1], self.width, self.height, fill=board_color, 
#             outline=board_color
#         )
#         canvas.widget_list[self.tk_id] = self
#         self._draw_roads(canvas)
#         
#         canvas.update()
            
#     def _draw_roads(self, canvas):
#         for road in self.road_dict.values():
#             road.draw(canvas)
            
#     def _erase_roads(self, canvas):
#         for road in self.road_dict.values():
#             road.erase(canvas)
                
#     def erase(self, canvas):
#         '''擦除路牌, 开始下一个1.6s的显示. 擦除路牌同时擦除所有路名'''
#         self._erase_roads(canvas)
#         canvas.delete(self.tk_id)    
    
        
class Road(object):
    name = ''           #路名   
    size = 15           #路名尺寸, 指字体大小, 单位px
    pos = 0, 0          #路名中心点在路牌上的位置坐标, 坐标会不断变化
    is_target = False   #是否是目标路名
    is_real = False     #是否真名
    
    def __init__(self, name, pos, size=15, is_target=False, is_real=False):
        self.name = name
        self.pos = pos
        self.size = size
        self.is_target = is_target
        self.is_real = is_real

    def __unicode__(self):
        return self.name, self.pos, self.is_target    
    
    def dist_with(self, a_road):
        '''计算路名间距'''
        return maths.dist(self.pos, a_road.pos)
    
    def reset_pos(self, target_road, algo):
        '''根据两点间距变化值, 重新计算当前路名位置坐标. 根据两点原有坐标可确定间距变化方向
        @param target_road: Road类型对象,
        @param algo: 问路变化算法, M r=0.5r, I r += 1  
        '''
        
        if algo == 'M':     #r = 0.5r
            pass
        elif algo == 'I': # r += 1    
            pass
        self.pos = 0, 1
    
#     def draw(self, canvas):
#         '''显示在屏幕上'''  #调用画布进行绘制...
#         road_font = DEFAULT_ROAD_FONT[0], self.size
#         road_color = TARGET_ROAD_COLOR if self.is_target else DEFAULT_ROAD_COLOR
#         self.tk_id = canvas.create_text(self.pos, text=self.name, fill=road_color, font=road_font)
#         canvas.widget_list[self.tk_id] = self 
        
#     def erase(self, canvas):
#         '''擦除路名'''
#         canvas.delete(self.tk_id)
    

