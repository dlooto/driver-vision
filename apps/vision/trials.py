#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

import random, threading
import maths
from config import *


CACHED_ROADS = [u'交大路', u'川大路', u'咚咚路', u'成创路', u'Mac路', 
                 u'胜利路', u'飞天路', u'乳香路', u'宁夏路', u'创业路']

def get_random_road(choice_roads):
        return random.choice(choice_roads)

class DemoThread(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        
    def run(self):
        print 'Demo thread started'
        while self.gui.is_started:
            self.gui.new_trial()
            
        print 'Demo thread stopped'    
        
        
class WatchPoint(object):
    tk_id = None
    pos = WATCH_POS
    radius = 5
    
    def __init__(self, pos=WATCH_POS, radius=5, fill=watch_color, outline=watch_color):
        self.pos = pos              #坐标点
        self.radius = radius        #圆圈半径
        self.fill = fill            #填充颜色
        self.outline = outline      #边框颜色
    
    def flash_data(self, pos=WATCH_POS):
        self.pos = pos
    
    def draw(self, canvas):
        self.tk_id = canvas.create_circle(self.pos[0], self.pos[1], self.radius, 
                                          fill=self.fill, outline=self.outline) #注视点
        canvas.widget_dict[self.tk_id] = self

class Board(object):
    '''路牌'''
    tk_id = None                #在画布上的id
    pos = 100, 100              #中心点坐标, 即路牌位置
    angle = 30                  #路牌初始角度, 在0,30, 60等中取值, 单位度
    width = 280                 #路牌宽度
    height = 200                #路牌高度
    
    road_dict = None            #路名列表
    target_road = None          #目标项
    
    #BOARD_POS[0], BOARD_POS[1], BOARD_SIZE['w'], BOARD_SIZE['h'], fill=board_color, outline=board_color
    def __init__(self, pos=BOARD_POS, width=BOARD_SIZE['w'], height=BOARD_SIZE['h'], angle=0):
        self.pos = pos
        self.width = width
        self.height = height
        self.angle = angle
        
        self.init_road_list(('A', 'D', 'H'), 'A')
    
    def move(self, dx, dy):
        '''路牌移动. dx = p2.x - p1.x, dy = p2.y - p1.y.
        erase()再draw(), 或者canvas.move(board)再canvas.move(roads)
        '''
        pass
    
    def flash_data(self, pos, roads_state, target, width=BOARD_SIZE['w'], height=BOARD_SIZE['h'], angle=0):
        ''' like roads_state=('A', 'D', 'H'), 'A' '''
        
        print pos, ':', roads_state, ':', target
        self.pos = pos
        self.width = width
        self.height = height
        self.angle = angle
        self.init_road_list(roads_state, target)
    
    def draw(self, canvas):
        '''显示在屏幕上'''  
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
        #canvas.after(3*1000)
        #canvas.update()        
        
        self._erase_roads(canvas)
        #canvas.after(3*1000)
        #canvas.update()
        
        canvas.delete(self.tk_id)
        #canvas.after(3*1000)
        #canvas.update()
    
    def init_road_list(self, marks, target):
        '''从DB随机选择num个路名, marks指定路名所在位置, 如('A', 'B', 'D', 'G')
        target表示目标项, 如target='B'
        '''
        print 'marks:', marks
        choice_roads = CACHED_ROADS
        self.road_dict = {}
        for mark in marks:
            road_name = get_random_road(choice_roads)
            self.road_dict[mark] = Road(road_name, self.pos_xx(mark))
            choice_roads.remove(road_name)
            print 'CACHED_ROADS: ', len(CACHED_ROADS)
            print 'choice_roads: ', len(choice_roads)
        self.target_road = self.road_dict.get(target)
        self.target_road.is_target = True   
    
    def clear_road_list(self):
        pass
    
    def set_target_road(self, mark): 
        self.road_dict.get(mark).is_target = True  
        
    def get_target_road(self):
        return self.target_road
    
    def get_road_num(self):
        return len(self.road_dict)
    
    # 获取A, B, C, D, E, F, G, H各点坐标
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
    pos = 0, 0          #路名中心点在路牌上的位置坐标
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



