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
import Queue


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
    
    pos = None                  #路牌中心点坐标
    width = 280                 #路牌宽度
    height = 200                #路牌高度
    
    road_dict = {}              #路名字典, key/value: 'A'/Road()
    target_seat = None          #目标路名位置
    
    # 辅助变量
    prompt_road_dict = {}
    road_que = Queue.Queue(maxsize=8)  #用于求数量阈值时路名的增减
    
    def __init__(self, e, a, road_size, width=BOARD_SIZE['w'], height=BOARD_SIZE['h']):
        ''' 
        @param e: 路牌中心距(路牌中心与注视点距离) 
        @param a: 路牌中心点与注视点连线的水平夹角(角度值)
        @param road_size: 路名尺寸
        '''
#         self.pos = self.calc_pos(e, a, wp_pos)
        self.width = width
        self.height = height
        
        # 根据尺寸确定各路名位置坐标参考系
        if self.width == 280:
            self.road_seat_refer = ROAD_SEAT
        elif self.width == 140:
            self.road_seat_refer = ROAD_SEAT_S
        else:
            self.road_seat_refer = ROAD_SEAT_B
        
        self.reset_pos(e, a)
        self.prompt_pos = WATCH_POS
        self._load_prompt_roads(road_size)  #各路名坐标计算依赖于self.pos
        
    def reset_pos(self, e, a, wp_pos=WATCH_POS):
        ''' 重置路牌中心点坐标.  路牌中心坐标一旦改变, 路牌上所有路名坐标将改变.
        
        e: 路牌中心距(路牌中心与注视点距离) 
        a: 路牌中心点与注视点连线的水平夹角(角度值) 
        wp_pos: 注视点坐标
        '''
        self.pos = self.calc_pos(e, a, wp_pos)
        
        #self.width = width
        #self.height = height
        
#         # 根据尺寸确定各路名位置坐标参考系
#         if self.width == 280:
#             self.road_seat_refer = ROAD_SEAT
#         elif self.width == 140:
#             self.road_seat_refer = ROAD_SEAT_S
#         else:
#             self.road_seat_refer = ROAD_SEAT_B
                                
    def reset_pos_xy(self, pos):
        ''' 重置路牌中心点坐标. 为reset_pos()的替代方法, 直接传入路牌中心点坐标.  
        路牌中心坐标一旦改变, 路牌上所有路名坐标将改变.
        
        @param pos: (x, y)元组形式坐标值 
        '''
        self.pos = pos
                                
        
    def clear_queue(self):
        '''清空queue, 用于下一轮求数量阈值的阶梯变化过程'''
        if not self.road_que.empty():
            self.road_que.queue.clear()
        
        # 单路牌求数量阈值: 路名上限为8, 初始路名显示条数为设定的值
        rest_seats = set(ALLOWED_ROAD_SEATS) - set(self.get_road_seats())
        for s in rest_seats:
            self.road_que.put(s)
        
    def calc_pos(self, e, a, wp_pos):
        '''根据初始参数e和a值, 计算路牌中心坐标
        @param e: 路牌中心与注视点距离
        @param a: 路牌中心点/注视点连线的水平夹角(角度值)
        '''
        x0, y0 = wp_pos
        return (x0 - e * math.cos(math.radians(a)), y0 - e * math.sin(math.radians(a)))
    
    def set_spared_road_seats(self, road_seats_item):
        '''设置待轮询的目标路名列表
        多路牌试验中添加该方法
        '''
        self.spared_road_seats = road_seats_item[0]    #路牌上路名标记 
        self.spared_target_seats = road_seats_item[1]  #待轮询的目标路名列表
    
    def load_roads(self, road_seats, target_seat, road_size):
        ''' 设置路牌上的所有路名. 从词库中重新随机选择, 路名对象将被重新初始化'''
        
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
        
    def _load_prompt_roads(self, road_size):
        ''' 加载8个位置上的全部路名, 用于提示目标项位置.'''
        
        self.prompt_road_dict.clear()
        modeled_roads = self.generate_random_roads(8)
        for mark in ALLOWED_ROAD_SEATS:
            road_model = random.choice(modeled_roads)
            self.prompt_road_dict[mark] = Road('%s: %s' % (mark, road_model.name), self.pos_xx(mark, road_size), 
                                        is_real=road_model.is_real, 
                                        size=road_size)
            modeled_roads.remove(road_model)
        
#     def flash_road_names(self, road_seats, target_seat):
#         '''仅刷新路名, 不替换路名对象, 不更新目标项及干扰项位置'''
#         modeled_roads = self.generate_random_roads(len(road_seats))
#         for mark in road_seats:
#             road_model = random.choice(modeled_roads)
#             self.road_dict[mark].name = road_model.name 
#             self.road_dict[mark].is_real = road_model.is_real #解决某个Bug
#             self.road_dict[mark].is_target = True if mark == target_seat else False
#             modeled_roads.remove(road_model)
#         self.target_seat = target_seat  
        
    def flash_road_names(self):
        '''仅刷新路名, 不替换路名对象, 不更新目标项及干扰项位置'''
        road_seats = self.get_road_seats()
        modeled_roads = self.generate_random_roads(len(road_seats))
        for mark in road_seats:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark].name = road_model.name 
            self.road_dict[mark].is_real = road_model.is_real #解决某个Bug
            modeled_roads.remove(road_model)
    
    def generate_random_roads(self, road_num):
        ''' 根据传入的路名数量, 生成不重复的随机路名列表.
         列表元素类型为Road Model(name, is_real).
        算法规则: 若路名数量为偶数, 则真假路名各一半, 若为奇数, 则假名多1.
        
        '''
        if road_num == 1:
            return random.sample(cached_kana_roads, 1)
            
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
        '''返回目标项与注视点连线夹角, 顺时针方向计算
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
        road_seats = self.get_road_seats()
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
    
    def update_flanker_numbers(self, is_left_algo, road_size):
        '''
        更新干扰项的数量. 该方法将修改road_dict字典对象. 
        若减少干扰项数, 则将路名位置标记放入队列, 否则从队列取出路名位置标记
        @param is_left_algo: 决定了干扰项数量是是+2还是-1
        @return: 返回更新后的干扰项数量
        '''
        if is_left_algo: #+2
            self.add_flankers(road_size)
        else:
            self.decr_flankers()
            
        #for m, road in self.road_dict:
        #    if road.
        #        self.road_dict.pop()    
        #self.road_que.put(item)
        #self.get_target_road()
    
    def add_flankers(self, road_size):
        '''增加干扰项数量'''
        if self.road_que.qsize() < 2:
            print('\nAlready max flankers on board: %s' % int(len(self.road_dict)-1))
            return            
        
        seat1, seat2 = self.road_que.get(), self.road_que.get() 
        road_model1, road_model2 = self.generate_random_roads(2)
        self.road_dict[seat1] = Road(road_model1.name, 
                                     self.pos_xx(seat1, road_size), 
                                     is_real=road_model1.is_real, 
                                     size=road_size
                                )
        self.road_dict[seat2] = Road(road_model2.name, 
                                     self.pos_xx(seat2, road_size), 
                                     is_real=road_model2.is_real, 
                                     size=road_size
                                )      
        
    def decr_flankers(self):
        '''减少干扰项数量'''
        if len(self.road_dict) == 2:
            print('\nAlready min flankers on board: %s' % int(len(self.road_dict)-1))
            return
        for seat in self.get_road_seats():
            if seat != self.target_seat:  #干扰项
                self.road_que.put(seat)
                self.road_dict.pop(seat)
                break
        
    
    def update_road_size(self, is_left_algo):
        '''更新路名尺寸.  
        @param is_left_algo: 决定了尺寸*1.2 or *0.8
        '''
        for road in self.road_dict.viewvalues():  #dict.values() Return a copy of the dictionary’s list of values
            road.reset_size(is_left_algo)    
    
    def get_road_size(self):
        '''返回路名当前尺寸'''
        return self.get_target_road().size
    
    def get_road_seats(self): #路名位置标记列表
        return self.road_dict.keys()
    
    def move(self, dx, dy):
        '''路牌移动. dx = p2.x - p1.x, dy = p2.y - p1.y.
        erase()再draw(), 或者canvas.move(board)再canvas.move(roads)
        '''
        pass
    
    def is_target_road_real(self):
        '''判断目标路名是否为真路名'''
        return self.get_target_road().is_real
    
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
        return self.pos[0]-self.road_seat_refer['left_x'], self.pos[1]+self.road_seat_refer['a_y']
    def pos_b(self, s):
        x, y = self.pos_a(s)
        return x, y+s+self.road_seat_refer['blank_y']
    def pos_c(self, s):
        x, y = self.pos_b(s)
        return x, y+s+self.road_seat_refer['blank_y']
    def pos_d(self, s=0):
        return self.pos[0]+self.road_seat_refer['right_x'], self.pos[1]+self.road_seat_refer['a_y']
    def pos_e(self, s):
        x, y = self.pos_d(s)
        return x, y+s+self.road_seat_refer['blank_y']
    def pos_f(self, s):
        x, y = self.pos_e(s)
        return x, y+s+self.road_seat_refer['blank_y']
    def pos_g(self, s):
        return self.pos[0], self.pos[1]-self.road_seat_refer['g_y']
    def pos_h(self, s):
        x, y = self.pos_g(s)
        return x, y+s+self.road_seat_refer['blank_y']
    
    
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

class MultiBoard(object):
    '''路牌容器, 内部管理着多个路牌'''
    
    
    board_dict = {} #路牌字典, {'B1':Board1, 'B2':Board2, 'B3':Board3} 
    
    prompt_board_dict = {}  #辅助变量, 用于提示目标项, 结构与board_dict相同
    board_que = Queue.Queue(maxsize=3)  #求数量阈值时路牌增减
    
    
    def __init__(self, param):
        '''初始化.  
        @param board_size:     3块路牌中的最大尺寸, 元组形式: (w, h) 
        @param board_range:    路牌排列形式, H-横, V-纵
        @param road_size:      路名尺寸
        @param pre_board_num: 求数量阈值时初始路牌显示数量
        @param board_space:   路牌间距
        @param board_scale:   路牌缩放比例, 默认1
        
        说明: 
            初始化路牌列表, 目标项提示路牌, 并设置目标路牌提示并相应路名,
        '''
        
        self.board_size = param.board_size
        self.board_range = param.board_range
        self.pre_board_num = param.pre_board_num
        self.road_size = param.road_size
        self.board_space = param.board_space
        self.board_scale = param.board_scale
        
        self.board_dict = self._generate_boards(param)      #初始化路牌
        
        self._init_prompt_boards(param.board_size, param.board_range, param.road_size, 
                                 param.board_space, param.board_scale)


    def reset_boards(self, eccent, angle): #TODO
        '''重新加载路牌: 路牌数量增减, 尺寸变化, 间距变化后路牌重新加载.
        包括: 重置各路牌坐标, 重新加载路牌上的路名对象.传入参数主要为目标路牌
        '''
        for k, b in self.board_dict.items():
            pass
        
    def _init_prompt_boards(self, board_size, board_range, road_size, board_space, board_scale):
        '''初始化3块提示路牌, 及加载路牌上相应的路名'''
        
        self.prompt_board_dict.clear()
        prev_board = None
        for i in range(3):
            width, height = board_size[0] * board_scale**i, board_size[1] * board_scale**i
            road_size = road_size * board_scale**i
            curr_board = Board(200, 0, road_size, width=width, height=height)  #第1个路牌注视点左移200
            if prev_board: #若当前为第2个/第3个路牌
                curr_board.reset_pos_xy(self._next_board_pos(
                                            prev_board.pos, 
                                            board_range, 
                                            board_space
                                        ))
                curr_board._load_prompt_roads(road_size)
            self.prompt_board_dict[ ALLOWED_BOARD_MARKS[i] ] = curr_board  
            
            prev_board = curr_board #指针下移
            
    def _generate_boards(self, param):
        '''根据初始参数设置, 生成路牌列表. '''
        board_dict = {}
        prev_board = None
        
        road_seats_list = param.get_multi_road_seats()
        for i in range(len(road_seats_list)):
            width = param.board_size[0] * param.board_scale**i
            height = param.board_size[1] * param.board_scale**i
            road_size = param.road_size * param.board_scale**i
            curr_board = Board(200, 0, road_size, width=width, height=height)  #第1个路牌注视点左移200
            if prev_board: #若当前为第2个/第3个路牌
                curr_board.reset_pos_xy(self._next_board_pos(
                                            prev_board.pos, 
                                            param.board_range, 
                                            param.board_space
                                        ))
                curr_board.set_spared_road_seats(road_seats_list[i])
            board_dict[ ALLOWED_BOARD_MARKS[i] ] = curr_board  
            
            prev_board = curr_board #指针下移   
                
        return board_dict                 
        
        
    def _next_board_pos(self, prev_board_pos, board_range, board_space):
        '''初始路牌排列时, 根据传入的前一个路牌坐标生成下一个路牌坐标
        @param prev_board_pos: 上一个生成的路牌中心坐标 
        @param board_range: 路牌排列方式, H-横, V-纵
        @param board_space: 路牌间距 
        
        @return: 返回下一个路牌中心坐标, (x,y)形式
        
        '''
        if board_range == 'H': #横
            return prev_board_pos[0]+board_space, prev_board_pos[1]
        else: #纵
            return prev_board_pos[0], prev_board_pos[1]+board_space
            
        
    def calc_ee(self, target_board, wpoint):
        '''计算目标路牌离心率: 根据目标项位置及注视点对象计算离心率
        @param target_board: 目标项位置标记, 如'A'
        @param wpoint: 注视点对象
        '''
        #return maths.dist(self.road_dict[target_seat].pos, wpoint.pos)
    
    def calc_angle(self, target_board, wpoint):
        '''计算目标路牌角度: 目标项与注视点连线夹角, 顺时针方向计算
        @param target_board: 目标项位置标记, 如'A'
        @param wpoint: 注视点对象  
        '''
        #return maths.angle(self.road_dict[target_seat].pos, wpoint.pos)       
    
    def set_target_board(self, board_key):
        '''B1/B2/B3'''
        self.target_board_key = board_key
    
    def get_target_board(self):
        '''获取目标路牌'''
        return self.target_board_key, self.board_dict[self.target_board_key]
            
            
    def get_target_road(self):
        '''获取目标路牌上的目标路名'''
        key, board = self.get_target_board()
        return board.get_target_road()            
            
    def get_target_name(self):
        key, board = self.get_target_board()
        return '%s,%s' % (key, board.get_target_road().name)
            
    def get_flanker_boards(self):
        pass     
    
    def flash_road_names(self):
        '''刷新所有路牌上的路名, 不替换路名对象'''
        for board in self.board_dict.values():
            board.flash_road_names()
        
class Road(object):
    name = ''           #路名   
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
        
    def reset_size(self, is_left_algo):
        '''重设路名尺寸'''
        if is_left_algo:
            if self.size*0.8 >= SIZE_BORDER[0]:
                self.size *= 0.8 
            else: 
                self.size = SIZE_BORDER[0]  
        else:
            if self.size*1.2 < SIZE_BORDER[1]:
                self.size *= 1.2
            else:
                self.size = SIZE_BORDER[1]
              
    
#     def draw(self, canvas):
#         '''显示在屏幕上'''  #调用画布进行绘制...
#         road_font = DEFAULT_ROAD_FONT[0], self.size
#         road_color = TARGET_ROAD_COLOR if self.is_target else DEFAULT_ROAD_COLOR
#         self.tk_id = canvas.create_text(self.pos, text=self.name, fill=road_color, font=road_font)
#         canvas.widget_list[self.tk_id] = self 
        
#     def erase(self, canvas):
#         '''擦除路名'''
#         canvas.delete(self.tk_id)
    

