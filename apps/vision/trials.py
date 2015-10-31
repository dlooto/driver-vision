#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

import random, threading
import maths
from config import *
from vision.models import Road, TrialParam


class WatchPoint(object):
    tk_id = None
    pos = WATCH_POS
    radius = 5
    
    def __init__(self, pos=WATCH_POS, radius=5, fill=watch_color, outline=watch_color):
        self.pos = pos              #坐标点
        self.radius = radius        #圆圈半径
        self.fill = fill            #填充颜色
        self.outline = outline      #边框颜色
    
    def flash_params(self, pos=WATCH_POS):
        self.pos = pos
    
    def draw(self, canvas):
        self.tk_id = canvas.create_circle(self.pos[0], self.pos[1], self.radius, 
                                          fill=self.fill, outline=self.outline) #注视点
        canvas.widget_dict[self.tk_id] = self


cached_real_roads = Road.objects.all_real_roads()
cached_kana_roads = Road.objects.all_kana_roads()

class Board(object):
    '''路牌'''
    
    trial_param = None
    
    tk_id = None                #路牌在画布上的id
    pos = BOARD_POS             #中心点坐标, 即路牌位置
    angle = 0                   #路牌初始角度, 在0,30, 60等中取值, 单位度
    width = 280                 #路牌宽度
    height = 200                #路牌高度
    
    road_dict = None            #路名列表
    target_road = None          #目标项
    
    def __init__(self, pos=BOARD_POS, road_seats=None, width=BOARD_SIZE['w'], height=BOARD_SIZE['h'], angle=0):
        self._load_params()
        
        self.pos = pos
        self.width = width
        self.height = height
        self.angle = angle
        
        self.init_road_dict(self.get_road_seats())
    
    def _load_params(self):
        '''从DB加载最新试验参数'''
        self.trial_param = TrialParam.objects.latest_coming()
        if not self.trial_param:
            raise Exception('trial_param is null')
    
    def save_control_params(self, demo_id): 
        '''向DB写入某次试验的控制参数'''   
        pass
    
    def generate_random_roads(self):
        ''' 获取不重复的随机路名列表, 列表元素类型为Road Model(name, is_real).
        算法规则: 若路名数量为偶数, 则真假路名各一半, 若为奇数, 则假名多1.
        
        '''
        num = self.get_road_num() / 2
        real_roads = random.sample(cached_real_roads, num)
        if self.trial_param.road_num % 2 == 1: #奇数
            real_roads.extend(random.sample(cached_kana_roads, num+1))
        else: #偶数
            real_roads.extend(random.sample(cached_kana_roads, num))            
                    
        return real_roads
        
    def get_road_num(self):
        return self.trial_param.road_num
    
    def get_target_seat(self):
        '''返回目标项位置标记, 如 'A'  '''
        return self.get_road_seats()[1]
        
    def get_road_seats(self):
        '''返回路名位置标记序列, 最后一个为目标项位置.
        @return: 元组, 如 ['A', 'B', 'D', 'E', 'H'], 'A'
        '''
        # rand_seats = random.sample(ALLOWED_ROAD_SEATS, self.get_road_num())  # just for test
        return self.trial_param.get_road_seats()
             
    def get_board_pos(self):
        return self.board_pos    
    
    def move(self, dx, dy):
        '''路牌移动. dx = p2.x - p1.x, dy = p2.y - p1.y.
        erase()再draw(), 或者canvas.move(board)再canvas.move(roads)
        '''
        pass
    
    def flash_params(self):
        ''''''
        ## do something to flash...
        
        # following just for testing...
        self.pos = self.pos[0], self.pos[1]-5
        self.init_road_dict(self.get_road_seats())

    def draw(self, canvas):
        '''显示在屏幕上'''  
        
        #绘制路牌
        self.tk_id = canvas.create_rectangle_pro(self.pos[0], self.pos[1], 
                                                 self.width, self.height, fill=board_color, outline=board_color)
        canvas.widget_dict[self.tk_id] = self
        self._draw_roads(canvas)
            
    def _draw_roads(self, canvas):
        for road in self.road_dict.values():
            road.draw(canvas)
            
    def _erase_roads(self, canvas):
        for road in self.road_dict.values():
            road.erase(canvas)            
                
    def erase(self, canvas):
        '''擦除路牌, 开始下一个1.6s的显示. 擦除路牌同时擦除所有路名'''
        self._erase_roads(canvas)
        canvas.delete(self.tk_id)
        #canvas.after(3*1000)
        #canvas.update()
    
    def init_road_dict(self, road_seats):
        ''' '''
        marks, target_mark = road_seats
        modeled_roads = self.generate_random_roads()

        self.road_dict = {}
        for mark in marks:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark] = Road(road_model.name, self.pos_xx(mark), is_real=road_model.is_real, size=self.trial_param.road_size)
            modeled_roads.remove(road_model)
        self.target_road = self.road_dict.get(target_mark)
        self.target_road.is_target = True   
    
    def clear_road_list(self):
        self.road_dict.clear()
    
    def set_target_road(self, mark): 
        self.road_dict.get(mark).is_target = True  
        
    def get_target_road(self):
        return self.target_road
    
    
    # 获取路牌上 A, B, C, D, E, F, G, H各点坐标
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
    
        
class Road(object):
    tk_id = None
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
    
    def draw(self, canvas):
        '''显示在屏幕上'''  #调用画布进行绘制...
        road_font = DEFAULT_ROAD_FONT[0], self.size
        self.tk_id = canvas.create_text(self.pos, text=self.name, fill=road_color, font=road_font)
        canvas.widget_dict[self.tk_id] = self 
        
    def erase(self, canvas):
        '''擦除路名'''
        canvas.delete(self.tk_id)            
    
    def dist_with(self, a_road):
        '''计算路名间距'''
        return maths.dist(self.pos, a_road.pos)
    
    def __unicode__(self):
        return self.name, self.pos, self.is_target
    
class Move():
    '''运动模式'''
    v = 1               #运动速率

class Tester():
    pass



