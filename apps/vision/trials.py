#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

import random
import maths
from config import *
from vision.models import RoadModel
import math


class WatchPoint(object):
    tk_id = None
    pos = WATCH_POS
    radius = 5
    
    def __init__(self, pos=WATCH_POS, radius=5, fill=watch_color, outline=watch_color):
        self.pos = pos              #坐标点
        self.radius = radius        #圆圈半径
        self.fill = fill            #填充颜色
        self.outline = outline      #边框颜色
    
cached_real_roads = RoadModel.objects.all_real_roads()
cached_kana_roads = RoadModel.objects.all_kana_roads()

class Board(object):
    '''路牌'''
    
    pos = None                  #中心点坐标, 即路牌位置
    width = 280                 #路牌宽度
    height = 200                #路牌高度
    
    road_dict = {}              #路名字典, key/value: 'A'/Road()
    target_seat = None
    
    # 辅助变量
    his_seats = []              #已被设定过的目标项位置列表
    
    def __init__(self, e, a, wp_pos=WATCH_POS, width=BOARD_SIZE['w'], height=BOARD_SIZE['h']):
        ''' 
        e: 路牌中心与注视点距离, 
        a: 路牌中心-注视点连线的水平夹角的角度值, 
        wp_pos: 注视点坐标
        '''
        self.pos = self.calc_pos(e, a, wp_pos)
        self.width = width
        self.height = height
        
    def calc_pos(self, e, a, wp_pos):
        '''计算路牌中心坐标, 根据初始参数e和a值
        @param e: 路牌中心与注视点距离
        @param a: 路牌中心-注视点连线的水平夹角的角度值 
        '''
        x0, y0 = wp_pos
        return (x0 - e * math.cos(math.radians(a)), y0 - e * math.sin(math.radians(a)))
    
    def load_roads(self, road_seats, target_seat, road_size):
        ''' 设置路牌上的所有路名. 每次从词库中重新随机选择'''
        
        self.road_dict.clear()
        modeled_roads = self.generate_random_roads(len(road_seats))
        for mark in road_seats:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark] = Road(road_model.name, self.pos_xx(mark, road_size), 
                                        is_real=road_model.is_real, 
                                        size=road_size)
            self.road_dict[mark].is_target = True if mark == target_seat else False
            modeled_roads.remove(road_model)
        self.target_seat = target_seat
        
    def flash_road_names(self, road_seats, target_seat):
        '''仅刷新路名, 不替换原有路名对象'''
        modeled_roads = self.generate_random_roads(len(road_seats))
        for mark in road_seats:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark].name = road_model.name 
            self.road_dict[mark].is_target = True if mark == target_seat else False
            modeled_roads.remove(road_model)
        self.target_seat = target_seat            
    
#     def next_target_seat(self):
#         '''切换目标项位置, 从目标'A' --> 'B', 
#         每调用一次, his_seats中添加一次已设置过的目标项位置, 如his_seats=['A', 'B']
#         '''
#         bak_targets = list(set(self.target_seats).difference(set(self.his_seats)))
#         target = random.choice(bak_targets)
#         self.his_seats.append(target)
#         return target
        
    def generate_random_roads(self, road_num):
        ''' 根据传入的路名数量, 生成不重复的随机路名列表.
         列表元素类型为Road Model(name, is_real).
        算法规则: 若路名数量为偶数, 则真假路名各一半, 若为奇数, 则假名多1.
        
        '''
        num = road_num / 2
        real_roads = random.sample(cached_real_roads, num) #先挑选一半的真路名列表
        if road_num % 2 == 1: #奇数
            num += 1
        real_roads.extend(random.sample(cached_kana_roads, num))            
                    
        return real_roads
        
    def get_ee(self, target_seat, wpoint):
        '''离心率: 根据目标项位置及注视点对象计算离心率
        @param target_seat: 目标项位置标记, 如'A'
        @param wpoint: 注视点对象  
        '''
        return maths.dist(self.road_dict[target_seat].pos, wpoint.pos)
    
    def get_angle(self, target_seat, wpoint):
        '''角度: 根据目标项位置及注视点对象计算两者角度
        @param target_seat: 目标项位置标记, 如'A'
        @param wpoint: 注视点对象  
        '''
        return maths.angle(self.road_dict[target_seat].pos, wpoint.pos)
    
    def get_road_spacings(self):
        if not hasattr(self, 'road_spacings') or not self.road_spacings:
            self.road_spacings = self.calc_target_flanker_spacings()
        return self.road_spacings    
    
    def calc_target_flanker_spacings(self):
        '''计算当前目标项与所有干扰项的间距, 返回间距列表'''
        target_road = self.get_target_road()
        flanker_roads = self.get_flanker_roads()
        road_spacings = []
        for f in flanker_roads:
            road_spacings.append(f.dist_with(target_road))
            
        return road_spacings  
    
    def update_flanker_poses(self, is_left_algo):
        '''更新所有干扰项的坐标, 在间距阶梯法中以反应目标与干扰项的间距变化. 
        算法规则: 根据两点原有坐标可确定间距变化方向, 目标路名坐标不变, 干扰路名则远离或靠近.
                以目标项为原点, 连线方向指向干扰项.
        '''
        target_road = self.road_dict[self.target_seat]
        road_seats = self.road_dict.keys()
        road_seats.remove(self.target_seat)
        
        for flanker_seat in road_seats:
            self.road_dict[flanker_seat].reset_pos(target_road, is_left_algo)
            
    def update_flanker_spacings(self, is_left_algo):
        '''根据算法更新所有干扰项-目标项间距值, 同时以目标项为基准, 更新所有干扰项的坐标'''
        
        road_spacings = self.get_road_spacings()    
        for i in range(len(road_spacings)):
            if is_left_algo:
                road_spacings[i] = round(0.5 * road_spacings[i], 2)
            else:
                road_spacings[i] += SPACING_RIGHT_DELTA
                  
        self.update_flanker_poses(is_left_algo)    
    
    def get_road_poses(self):
        '''返回所有路名坐标, Test...'''
        poses = []
        for road in self.road_dict.values():
            poses.append(road.pos)
        return poses    
    
    def move(self, dx, dy):
        '''路牌移动. dx = p2.x - p1.x, dy = p2.y - p1.y.
        erase()再draw(), 或者canvas.move(board)再canvas.move(roads)
        '''
        pass
    
    def is_target_road_real(self):
        '''判断目标路名是否为真路名'''
        target_road = self.road_dict[self.target_seat]
        return target_road.is_real  
    
    def get_target_road(self):
        return self.road_dict[self.target_seat]
    
    def get_flanker_roads(self):
        '''返回干扰路名列表'''
        target_road = self.get_target_road()
        roads = self.road_dict.values()
        roads.remove(target_road)
        return roads
  
    def pos_xx(self, mark, s):
        '''以路牌中心坐标为参照点, 获取路牌上 A, B, C, D, E, F, G, H各点中心坐标
        @param mark: 路名位置标识, 一般为小写字母, 以匹配正确的pos_x方法
        @param s:  路名尺寸(一般为高度值)
        '''
        mt = 'pos_%s' % mark.lower()
        return getattr(self, mt)(s)    
    
    def pos_a(self, s=0):#带默认值可不传, 为便于里pos_xx调用的一致性
        return self.pos[0]-ROAD_SEAT['left_x'], self.pos[1]+ROAD_SEAT['a_y']
    def pos_b(self, s):
        x, y = self.pos_a(s)
        return x, y+s+ROAD_SEAT['blank_y']
    def pos_c(self, s):
        x, y = self.pos_b(s)
        return x, y+s+ROAD_SEAT['blank_y']
    def pos_d(self, s=0):
        return self.pos[0]+ROAD_SEAT['right_x'], self.pos[1]+ROAD_SEAT['a_y']
    def pos_e(self, s):
        x, y = self.pos_d(s)
        return x, y+s+ROAD_SEAT['blank_y']
    def pos_f(self, s):
        x, y = self.pos_e(s)
        return x, y+s+ROAD_SEAT['blank_y']
    def pos_g(self, s):
        return self.pos[0], self.pos[1]-ROAD_SEAT['g_y']
    def pos_h(self, s):
        x, y = self.pos_g(s)
        return x, y+s+ROAD_SEAT['blank_y']
    
    
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
    size = 15           #默认路名尺寸, 指字体大小, 单位px
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
        '''计算路名间距, 结果取2位小数'''
        return maths.dist(self.pos, a_road.pos)
    
    def reset_pos(self, target_road, is_left_algo):
        '''根据两点间距变化值, 重新计算当前路名位置坐标. 
        根据两点原有坐标可确定间距变化方向, 目标路名坐标不变, 干扰路名则远离或靠近
        @param target_road: Road类型对象,
        @param is_left_algo: 算法参数, True-0.5r, False-r+1
        '''
        
        x0, y0 = target_road.pos
        x, y = self.pos
        r = maths.dist((x0, y0), (x, y)) #两路名原来的间距
        if is_left_algo:
            r1 = 0.5*r
        else:
            r1 = r + SPACING_RIGHT_DELTA
                        
        x = x0 - r1*(x0-x)/r*1.0
        y = y0 - r1*(y0-y)/r*1.0
        self.pos = round(x,2), round(y,2)
    
#     def draw(self, canvas):
#         '''显示在屏幕上'''  #调用画布进行绘制...
#         road_font = DEFAULT_ROAD_FONT[0], self.size
#         road_color = TARGET_ROAD_COLOR if self.is_target else DEFAULT_ROAD_COLOR
#         self.tk_id = canvas.create_text(self.pos, text=self.name, fill=road_color, font=road_font)
#         canvas.widget_list[self.tk_id] = self 
        
#     def erase(self, canvas):
#         '''擦除路名'''
#         canvas.delete(self.tk_id)
    

