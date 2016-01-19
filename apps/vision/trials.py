#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

import Queue
import random
import maths
from config import *
from vision.models import RoadModel


cached_real_roads = RoadModel.objects.all_real_roads()
cached_kana_roads = RoadModel.objects.all_kana_roads()

class WatchPoint(object):
    pos = WATCH_POS
    radius = 5
    
    def __init__(self, pos=WATCH_POS, radius=5, fill=watch_color, outline=watch_color):
        #坐标点. 在圆周运动过程中, 该值为原始坐标, 作为运动圆心代入计算
        self.pos = pos               
        
        #运动过程中, 该值为运动坐标. 绘制时以该坐标为准
        self.move_pos = pos         
        
        self.radius = radius        #圆圈半径
        self.fill = fill            #填充颜色
        self.outline = outline      #边框颜色
    
    def set_move_scheme(self, move_scheme):
        self.move_scheme = move_scheme
        
    def move(self): 
        self.move_pos = self.move_scheme.new_wp_pos(self.move_pos)  

class BaseBoard(object):
    
    #def __init__(self):
    #    pass
    
    def set_move_scheme(self, move_scheme):
        self.move_scheme = move_scheme 
        
        if self.move_scheme:
            self.move_scheme.print_direct()
            
    def set_move_velocity(self, velocity):
        '''静态试验中重写该方法为空'''
        if not self.move_scheme:
            return
        self.move_scheme.set_velocity(velocity)  

    def get_move_velocity(self):
        '''静态试验中重写该方法为空'''
        return self.move_scheme.get_velocity()         
        
    def change_move_direction(self):
        self.move_scheme.change_direction()     
        
    def change_items_velocity(self, is_left_algo): #动态敏感度阈值时速度阶梯变化
        v0 = self.get_move_velocity()
        if is_left_algo:
            if v0*VELO_PARAM['left'] > VELO_BORDER['max']:
                self.set_move_velocity(VELO_BORDER['max'])
            else:
                self.set_move_velocity(v0*VELO_PARAM['left'])
        else: 
            if v0*VELO_PARAM['right'] < VELO_BORDER['min']:
                self.set_move_velocity(VELO_BORDER['min'])
            else:
                self.set_move_velocity(v0*VELO_PARAM['right'])
               

class ItemQueue():
    '''队列, 主用于路名或路牌增减. 默认规则: 增加路牌/路名以最近的间距增加(表现为出队列)，
    减少路牌/路名以最远的间距减少(表现为入队列).'''
    
    def __init__(self, board, maxsize=8):
        '''
        @param maxsize: 队列长度    
        '''
        self.maxsize = maxsize
        self._queue = []
        self.board = board  #单路牌或多路牌
                   
    def empty(self):
        '''判断队列是否为空'''
        if not self._queue or len(self._queue) == 0:
            return True
        return False
    
    def clear(self):
        '''清空队列'''
        self._queue = []
    
    def get(self):
        pass
    
    def put(self, item):
        '''入队列'''
        if self.qsize() >= self.maxsize:
            print self._queue
            raise Exception('%s beyond largest size: %s' % (self.qsize(), self.maxsize))
        self._queue.append(item)
        
    def qsize(self):
        '''返回队列长度'''
        return len(self._queue)
    
    def bget(self):
        '''从队列中获取离目标项位置最近(间距最小)的位置返回, 并移除队列中相应元素'''
        min_space = 99999999
        min_seat = self._queue[0]
        for seat in self._queue:
            space = self.board.calc_queue_space(seat) 
            if space < min_space:
                min_space = space
                min_seat = seat
        self._queue.remove(min_seat)
        return min_seat  
        
               
class Board(BaseBoard):
    '''路牌'''
    
    def __init__(self, e, a, road_size, width=BOARD_SIZE['w'], height=BOARD_SIZE['h']):
        ''' 
        @param e: 路牌中心距(路牌中心与注视点距离) 
        @param a: 路牌中心点与注视点连线的水平夹角(角度值)
        @param road_size: 路名尺寸
        '''
        
        BaseBoard.__init__(self)
        
        #辅助变量
        #road_que = Queue.Queue(maxsize=8)  #用于求数量阈值时路名的增减
        self.road_que = ItemQueue(self, maxsize=8)  #用于求数量阈值时路名的增减
        
        self.pos = None                  #路牌中心点坐标
        self.road_dict = {}              #路名字典, key/value: 'A'/Road()
        self.target_seat = None          #目标路名位置
        
        self.width = width
        self.height = height
        self.road_size = road_size
        
        # 根据尺寸确定各路名位置坐标参考系. 以140宽为基准
        self.road_seat_refer = scale_refer(width/140.0)
        
        self.reset_pos(e, a)
        #self.prompt_pos = WATCH_POS
        
        self.prompt_road_dict = {}
        self._load_prompt_roads(road_size)  #提示路牌上的各路名坐标计算依赖于self.pos
        
    def __str__(self):
        return '%s, (%s, %s)' % (self.pos, self.width, self.height)    
        
        
    def reset_pos(self, e, a, wp_pos=WATCH_POS):
        ''' 重置路牌中心点坐标.  路牌中心坐标一旦改变, 重新加载路名后路牌上所有路名坐标将改变.
        
        e: 路牌中心距(路牌中心与注视点距离) 
        a: 路牌中心点与注视点连线的水平夹角(角度值) 
        wp_pos: 注视点坐标
        '''
        self.pos = self.calc_pos(e, a, wp_pos)
        
                         
    def reset_size(self, is_left_algo):
        '''重设路牌尺寸'''
        original_width = self.width 
        
        if is_left_algo:
            if self.width * SIZE_PARAM['left'] < BOARD_SIZE_BORDER['min'][0] or \
                    self.height * SIZE_PARAM['left'] < BOARD_SIZE_BORDER['min'][1]:
                self.width, self.height = BOARD_SIZE_BORDER['min']
            else:
                self.width, self.height = self.width * SIZE_PARAM['left'], self.height * SIZE_PARAM['left']    
        else:
            if self.width * SIZE_PARAM['right'] > BOARD_SIZE_BORDER['max'][0] or \
                    self.height * SIZE_PARAM['right'] > BOARD_SIZE_BORDER['max'][1]:
                self.width, self.height = BOARD_SIZE_BORDER['max']            
            else:
                self.width, self.height = self.width * SIZE_PARAM['right'], self.height * SIZE_PARAM['right']
                
        #路牌尺寸变化将引起路牌上路名尺寸同比例变化
        self.road_size = self.road_size*self.width*1.0 / original_width
                                
    def reset_pos_xy(self, pos):
        ''' 重置路牌中心点坐标. 为reset_pos()的替代方法, 直接传入路牌中心点坐标.  
        路牌中心坐标一旦改变, 后续逻辑需要重新加载路牌上的路名(调整路名坐标).
        
        @param pos: (x, y)元组形式坐标值 
        '''
        self.pos = pos
                                
        
    def clear_queue(self):
        '''清空queue, 用于下一轮求数量阈值的阶梯变化过程'''
        if not self.road_que.empty():
            self.road_que.clear()
        
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
        
    def load_roads_lean(self, road_size):
        ''' 多路牌试验时加载路牌上的所有路名. 从词库中重新随机选择, 路名对象将被重新初始化, 
        不设置目标路名
        '''
        
        self.road_dict.clear()
        modeled_roads = self.generate_random_roads(len(self.spared_road_seats))
        for mark in self.spared_road_seats:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark] = Road(road_model.name, self.pos_xx(mark, road_size), 
                                        is_real=road_model.is_real, 
                                        size=road_size)
            modeled_roads.remove(road_model)
        
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
        
        
    def flash_road_names(self):
        '''仅刷新路名, 不替换路名对象, 不更新目标项及干扰项位置'''
        road_seats = self.get_road_seats()
        modeled_roads = self.generate_random_roads(len(road_seats))
        for mark in road_seats:
            road_model = random.choice(modeled_roads)
            self.road_dict[mark].name = road_model.name 
            self.road_dict[mark].is_real = road_model.is_real #解决某个Bug
            modeled_roads.remove(road_model)
            
    def update_road_poses(self):     
        '''路牌移动时更新所有路名坐标'''   
        pass
    
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
    
    def get_item_spacings(self):
        '''返回目标项与干扰项间距: 与multiBoard形成多态'''
        return self.get_road_spacings()   
    
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
            self.road_dict[flanker_seat].update_pos(target_road.pos, is_left_algo)
            
    def update_flanker_spacings(self, is_left_algo, update_all=False):
        '''以目标项为基准, 更新所有干扰项的坐标.(即更新了干扰项与目标项的间距)
        @param is_left_algo: 算法规则, true-流程图左侧看法, 一般设置为间距减小, false-右侧算法, 设置为间距增加
        @param update_all: true-间距统一变化, 
                          false-间距不统一变化, 规则: 若为左侧算法, 则减小最大间距; 若为右侧算法, 则增加最小间距 
        '''
        if update_all: #若所有干扰项间距统一变化 
            self.update_flanker_poses(is_left_algo)
            return
        
        target_road = self.get_target_road()
        space_dict = self.get_flanker_space_dict()
        if is_left_algo:    #选择最大的间距进行减小
            mflanker, mval = self.get_max_space_flanker(space_dict)        
        else:       #选择最小的间距进行间距增加
            mflanker, mval = self.get_min_space_flanker(space_dict)
               
        #筛选出间距与最大值或最小值相等的路名
        equal_space_roads  = [] #间距相等的路名列表
        for road, space in space_dict.items():
            if abs(space-mval) < 0.01:
                equal_space_roads.append(road)  
                         
        for flanker in equal_space_roads:
            flanker.update_pos(target_road.pos, is_left_algo)
                
    def get_flanker_space_dict(self):
        '''返回干扰项与目标项间距字典, 干扰项对象为key, 值为间距值. 主要用于计算最大间距及最小间距'''
        space_dict = {}
        target_road = self.get_target_road()
        for flanker in self.get_flanker_roads():
            space_dict[flanker] = flanker.dist_with(target_road)
        return space_dict            
                
    def get_max_space_flanker(self, space_dict):
        '''返回与目标项间距最大的干扰项'''
        mval = 0.0
        mflanker = None
        for flanker, space in space_dict.items():
            if space > mval:
                mval = space
                mflanker = flanker
        
        return mflanker, mval        

    def get_min_space_flanker(self, space_dict):
        '''返回与目标项间距最大的干扰项''' 
        mval = 99999999
        mflanker = None
        for flanker, space in space_dict.items():
            if space < mval:
                mval = space
                mflanker = flanker
        
        return mflanker, mval                                 
                        
                
    def update_flanker_numbers(self, is_left_algo):
        '''
        更新干扰项的数量. 该方法将修改road_dict字典对象. 
        若减少干扰项数, 则将路名位置标记放入队列, 否则从队列取出路名位置标记
        @param is_left_algo: 决定了干扰项数量是是+2还是-1
        @return: 返回更新后的干扰项数量
        '''
        if is_left_algo: #+2
            self.add_flankers()
        else:
            self.decr_flankers()
          
    def calc_queue_space(self, seat):
        '''用于数量阈值队列中求目标项与当前位置对象的间距'''
        return maths.dist(self.get_target_road().pos, self.pos_xx(seat, self.road_size))         
          
    def add_flankers(self):
        '''增加干扰项数量, 每次增加2个干扰项. 增加以最近间距位置开始增加'''
        if self.road_que.qsize() < 2:
            print('\nAlready max flankers on board: %s' % int(len(self.road_dict)-1))
            return            
        
        road_model1, road_model2 = self.generate_random_roads(2)
        seat1, seat2 = self.road_que.bget(), self.road_que.bget()
        
        self.road_dict[seat1] = Road(road_model1.name, 
                                     self.pos_xx(seat1, self.road_size), 
                                     is_real=road_model1.is_real, 
                                     size=self.road_size
                                )
        self.road_dict[seat2] = Road(road_model2.name,
                                     self.pos_xx(seat2, self.road_size),
                                     is_real=road_model2.is_real,
                                     size=self.road_size
                                )
        
    def decr_flankers(self):
        '''减少干扰项数量, 每次减少1个. 从当前已存在的路名列表中最大间距的干扰项开始减少'''
        if len(self.road_dict) == 2:
            print('\nAlready min flankers on board: %s' % int(len(self.road_dict)-1))
            return
        
        space_dict = self.get_flanker_space_dict()
        max_flanker, max_space = self.get_max_space_flanker(space_dict)
        
        for seat, road in self.road_dict.items():
            if seat != self.target_seat and road == max_flanker:
                self.road_que.put(seat)
                self.road_dict.pop(seat)
                break
    
    def update_items_size(self, is_left_algo):
        '''与MultiBoard形成多态而增加, 在algo中调用, 用于计算尺寸阈值中更新阶梯变量'''
        self.update_road_size(is_left_algo)
    
    def update_road_size(self, is_left_algo):
        '''更新路名尺寸.  
        @param is_left_algo: 决定了尺寸用左边算法计算 or 右边算法计算
        '''
        for road in self.road_dict.viewvalues():
            road.reset_size(is_left_algo)    
    
    def get_road_size(self):
        '''返回路名当前尺寸'''
        return self.get_target_road().size
    
    def get_item_size(self):
        '''返回路名尺寸, 为与MultiBoard形成多态调用而增加'''
        return '%s' % self.get_road_size()
    
    def get_road_seats(self): #路名位置标记列表
        return self.road_dict.keys()
    
    def count_flanker_items(self):
        '''返回干扰项数量'''
        return len(self.get_road_seats()) - 1
    
    def move(self):
        ''' 移动路牌坐标
        @param move_scheme: 运动模式对象
        '''
        new_pos = self.move_scheme.new_pos(self.pos)
        dx, dy = new_pos[0]-self.pos[0], new_pos[1]-self.pos[1] #路名偏移量
        self.reset_pos_xy(new_pos)
        
        for road in self.road_dict.values():
            road.pos = road.pos[0]+dx, road.pos[1]+dy
    
    
    def dist_with(self, a_board):
        '''计算路牌间距, 结果取2位小数. 以路牌中心点为参考
        @param a_board: 传入的参数路牌对象
        
        @return: 返回间距值
        '''
        return maths.dist(self.pos, a_board.pos)
    
    def update_pos(self, target_pos, is_left_algo):
        '''根据两点间距变化值, 重新计算当前路名/路牌坐标. 
        根据两点原有坐标可确定间距变化方向, 目标项坐标不变, 干扰项则远离或靠近
        @param target_pos: 目标项位置坐标, 元组对象(x, y)
        @param is_left_algo: 算法参数, 如 True=0.5r, False=r+1
        '''
        
        x0, y0 = target_pos
        x, y = self.pos
        r = maths.dist((x0, y0), (x, y)) #计算两点间距
        if is_left_algo:
            r1 = r * SPACING_PARAM['left']
        else:
            r1 = r + SPACING_PARAM['right']
                        
        x = x0 - r1*(x0-x)/r*1.0
        y = y0 - r1*(y0-y)/r*1.0
        self.pos = round(x,2), round(y,2)        
    
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
    
    ## 以下建立路牌及路名坐标系  
    def pos_xx(self, mark, s):
        '''以路牌中心坐标为参照点, 获取路牌上 A, B, C, D, E, F, G, H各点中心坐标
        @param mark: 路名位置标识, 一般为小写字母, 以匹配正确的pos_x方法
        @param s:  路名尺寸(一般为文本高度值)
        '''
        mt = 'pos_%s' % mark.lower()
        return getattr(self, mt)(s)    
    
    def pos_a(self, s=0):#带默认值时可不传, 为便于pos_xx调用的一致性
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

class MultiBoard(BaseBoard):
    '''路牌容器, 内部管理着多个路牌'''
    
    def __init__(self, param):
        '''初始化.  
        @param board_size:     3块路牌中的最大尺寸, 元组形式: (w, h) 
        @param board_range:    路牌排列形式, H-横, V-纵
        @param road_size:      初始路名尺寸, 一般为第一个最大路牌上的路名尺寸
        @param pre_board_num:  求数量阈值时初始路牌显示数量
        @param board_space:   路牌间距
        @param board_scale:   路牌缩放比例, 默认1
        
        说明: 
            初始化路牌列表, 目标项提示路牌, 并设置目标路牌提示并相应路名,
        '''
        BaseBoard.__init__(self)
        
        # 辅助变量
        #board_que = Queue.Queue(maxsize=3)  #求数量阈值时路牌增减
        self.board_que = ItemQueue(self, maxsize=6)  #作用于求数量阈值时路牌增减, 存放路牌标识位
        
        #辅助变量, 用于提示目标项, 结构与board_dict相同
        self.prompt_board_dict = {} 
        
        self.board_size = param.get_board_size()
        self.board_range = param.board_range
        self.pre_board_num = param.pre_board_num
        self.road_size = param.road_size        #最大路名尺寸
        self.board_space = param.board_space
        self.board_scale = param.board_scale
        
        # 初始化路牌字典, 该字典存放正在控制过程中并显示的路牌, 如 {'B1':Board1, 'B2':Board2, 'B3':Board3}
        # 已初始化且未显示的路牌将存放于 board_que
        self.board_repos = self._generate_boards(param)   #路牌仓库, 存储所有待用路牌   
        
        #初始化为空, 在控制过程中真正在使用的路牌, 从board_repos中装载
        self.board_dict = {} 
        self.reload_boards()  #装载self.board_dict
        
        self._init_prompt_boards(param.get_board_size(), param.board_range, param.road_size, 
                                 param.board_space, param.board_scale)

    def reload_boards(self):
        '''每一轮目标项变化后重新加载路牌, 主要因路牌数量阈值情况而增加 '''
        self.board_dict.clear()
        for k, board in self.board_repos.items():
            self.board_dict[k] = board 

    # 根据当前self.board_dict中路牌情况(数量, 排列状况等)来设置坐标...
    def reset_boards(self, eccent, angle, ): 
        '''重设路牌坐标
        
        @param eccent: 最大路牌的离心率, 该路牌作为其他路牌的参考路牌
        @param angle:  最大路牌的角度
        '''
        
        board_marks = ALLOWED_BOARD_MARKS
        prev_board = None
        for i in range(len(board_marks)):
            curr_board = self.board_dict[board_marks[i]]
            curr_board.reset_pos(eccent, angle)
            if prev_board: #True-表示第2/3个路牌
                curr_board.reset_pos_xy(self._next_board_pos(
                                            prev_board.pos, 
                                            self.board_range, 
                                            self.board_space
                                        ))
            prev_board = curr_board     #指针下移    
        
        
    def load_roads(self, target_board_key, target_seat):
        ''' 多个路牌上加载所有路名, 并根据条件设置目标项
        
        @param target_board_key: 目标路牌位置标记
        @param target_seat: 目标路名位置
        '''
        for iboard in self.board_dict.values():
            if iboard == self.board_dict[target_board_key]: #是目标路牌
                iboard.load_roads(iboard.spared_road_seats, target_seat, iboard.road_size)
            else:
                iboard.load_roads_lean(iboard.road_size)    
        
    def _init_prompt_boards(self, board_size, board_range, road_size, board_space, board_scale):
        '''初始化每一次阶梯算法的目标提示路牌, 并加载路牌上相应的路名'''
        
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
            curr_board._load_prompt_roads(road_size) #路牌坐标重设后重新加载路名
            self.prompt_board_dict[ ALLOWED_BOARD_MARKS[i] ] = curr_board  
            
            prev_board = curr_board #指针下移
            
    def _generate_boards(self, param):
        '''生成初始路牌列表. 全部路牌都被加载'''
        board_dict = {}
        prev_board = None
        
        road_seats_list = param.get_multi_road_seats()
        board_size = param.get_board_size()
        for i in range(len(road_seats_list)): #3个路牌同时初始化
            width = board_size[0] * param.board_scale**i
            height = board_size[1] * param.board_scale**i
            road_size = param.road_size * param.board_scale**i
            curr_board = Board(200, 0, road_size, width=width, height=height)  #第1个路牌注视点左移200
            if prev_board: #若当前为第2个/第3个路牌
                curr_board.reset_pos_xy(self._next_board_pos(
                                            prev_board.pos, 
                                            param.board_range, 
                                            param.board_space
                                        ))
                #print 'board pos: ', curr_board.pos
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
            
        
    def calc_ee(self, wpoint):
        '''计算目标路牌离心率: 根据目标路牌中心点及注视点对象计算离心率
        @param target_board: 目标路牌
        @param wpoint: 注视点对象
        '''
        key, target_board = self.get_target_board()
        return maths.dist(target_board.pos, wpoint.pos)
        
    
    def calc_angle(self, wpoint):
        '''计算目标路牌角度: 目标路牌中心点与注视点连线夹角, 顺时针方向计算
        @param target_board: 目标路牌对象
        @param wpoint: 注视点对象  
        '''
        key, target_board = self.get_target_board()
        return maths.angle(target_board.pos, wpoint.pos)       
    
    def set_target_board(self, board_key):
        '''B1/B2/B3'''
        self.target_board_key = board_key
    
    def get_target_board(self, target_board_key=None):
        '''获取目标路牌'''
        if target_board_key:
            return target_board_key, self.board_dict[target_board_key]
        return self.target_board_key, self.board_dict[self.target_board_key] #目标路牌必定存在于dict中
            
    def get_spared_target_seats(self, board_key):
        '''返回当前设定的目标路牌上的待轮询目标路牌路名位置'''
        return self.board_repos[board_key].spared_target_seats
            
    def get_target_road(self):
        '''获取目标路牌上的目标路名'''
        key, board = self.get_target_board()
        return board.get_target_road()            
            
    def get_target_name(self, target_board_key=None):
        key, board = self.get_target_board(target_board_key)     
        return '%s:%s' % (key, board.get_target_road().name)
            
    def get_flanker_boards(self):
        flanker_boards = self.board_dict.values()
        key, iboard = self.get_target_board()
        flanker_boards.remove(iboard)
        return flanker_boards
    
    def count_flanker_items(self):
        '''返回干扰项数量'''
        return len(self.board_dict) - 1 
    
    def get_item_size(self):
        '''返回路牌尺寸, 为与Board形成多态调用而增加. 目前仅返回最大路牌尺寸
        @return: width, height
        '''
        return '%s,%s' % (self.board_size[0], self.board_size[1])
    
    def get_item_spacings(self):
        '''返回目标项与干扰项间距: 与Board类型对象形成多态'''
        return self._calc_item_spacings()
    
    def _calc_item_spacings(self):
        '''计算当前目标路牌与所有干扰路牌的间距. 路牌坐标变化将引起间距变化
        @return: 间距列表
        '''
        key, iboard = self.get_target_board()
        spacings = []
        for board in self.get_flanker_boards():
            spacings.append(board.dist_with(iboard))
            
        return spacings
        
    def clear_queue(self):  #TODO: 不可以清空已重设坐标后的boards
        '''数量阈值时清空queue
        
        用于下一轮求数量阈值的阶梯变化过程
        '''
        if not self.board_que.empty():
            self.board_que.clear()
        
        # 阶梯循环前装载pre_board_num数量的路牌(包括目标项). 注: 此处不可以进行board_dict.clear(), 
        # 因为各路牌坐标已进行了重设.
        while len(self.board_dict) > self.pre_board_num:
            self.decr_board()
        
        # 剩余路牌位置标记存入board_que    
        rest_marks = set(ALLOWED_BOARD_MARKS) - set(self.board_dict.keys())
        for m in rest_marks:
            self.board_que.put(m)
           
    def update_flanker_numbers(self, is_left_algo):
        if is_left_algo:
            self.incre_board()
        else:
            self.decr_board()            
    
    def calc_queue_space(self, seat):
        '''board_que中使用, 计算路牌间隔, 如若目标为B1, 则B3与B1间隔为2, B5与B1间隔为4'''
        return abs(int(seat[1]) - int(self.target_board_key[1]))
           
    def incre_board(self): #该方法现仅适用于3个路牌情况
        '''board_dict中增加路牌, 目前每次仅增加一块路牌. 增加的路牌为离目标路牌最近的位置'''
        if self.board_que.qsize() < 1:
            return
        key = self.board_que.bget()
        self.board_dict[key] = self.board_repos[key]
    
    def decr_board(self): #该方法已比较通用, 可适用于路牌数大于3个情况
        '''board_dict中减少一块路牌. 去除的路牌为离目标项最远的位置'''
        if len(self.board_dict) == 2: #至少2个路牌
            return
        
        # 得到距离目标项最远的干扰路牌
        max_space = 0.0
        max_fboard = None
        key, tboard = self.get_target_board()
        for fboard in self.get_flanker_boards():
            space = tboard.dist_with(fboard)
            if space > max_space: 
                max_space = space
                max_fboard = fboard
                
        for key, board in self.board_dict.items():
            if key == self.target_board_key: #目标路牌不允许去除
                continue
            if board == max_fboard:
                self.board_dict.pop(key)
                self.board_que.put(key)
                return
    
    def update_flanker_spacings(self, is_left_algo, update_all=False):
        '''求多路牌关键间距时调用.
        根据算法更新所有目标项-干扰项间距值, 本质上是更新干扰项的坐标(以目标项为原点)'''
        
        if update_all:
            self.update_flanker_poses(is_left_algo)
            return
        
        space_dict = {}
        key, iboard = self.get_target_board()
        for flanker in self.get_flanker_boards():
            space_dict[flanker] = flanker.dist_with(iboard)    
        
        if is_left_algo:    #选择最大的间距进行减小
            mval = 0.0
            for space in space_dict.values():
                if space > mval:
                    mval = space
        else:       #选择最小的间距进行间距增加
            mval = 99999999
            for space in space_dict.values():
                if space < mval:
                    mval = space 
 
        #筛选出间距与最大值或最小值相等的路牌
        equal_space_boards  = [] #间距相等的路牌列表
        for board, space in space_dict.items():
            if abs(space-mval) < 0.01:
                equal_space_boards.append(board)               
        for flanker_board in equal_space_boards:
            flanker_board.update_pos(iboard.pos, is_left_algo)
            flanker_board.load_roads_lean(flanker_board.road_size)                            
        
    
    def update_flanker_poses(self, is_left_algo):
        '''更新所有干扰项的坐标: 在间距阶梯法中用来反应目标与干扰项的间距变化. 
        算法规则: 根据两点原有坐标可确定间距变化方向, 目标路名坐标不变, 干扰路名则远离或靠近.
                以目标项为原点, 连线方向指向干扰项.
        '''
        key, iboard = self.get_target_board()
        for flanker_board in self.get_flanker_boards():
            flanker_board.update_pos(iboard.pos, is_left_algo)
            
            # 路牌位置变化后需重新加载路名
            flanker_board.load_roads_lean(flanker_board.road_size)  
        
    def update_items_size(self, is_left_algo):
        '''更新路牌尺寸.  
        2种变化规则: 1. 路牌尺寸独立变化, 2.路牌尺寸与间距同比例变化.  目前暂实现第1种
        路牌尺寸变化, 是否要引起其他参数变化? TODO...
        
        @param is_left_algo: 决定了尺寸用左边算法计算 or 右边算法计算
        '''
        for board in self.board_dict.values():
            board.reset_size(is_left_algo)
            board.load_roads_lean(board.road_size)
        
    def flash_road_names(self):
        '''刷新所有路牌上的路名, 不替换路名对象'''
        for board in self.board_dict.values():
            board.flash_road_names()
            
    def is_target_road_real(self):
        key, iboard = self.get_target_board()
        return iboard.is_target_road_real()      
    
    def move(self):
        ''' 移动路牌坐标
        '''
        key, iboard = self.get_target_board()
        
        new_pos = self.move_scheme.new_pos(iboard.pos)
        dx, dy = new_pos[0]-iboard.pos[0], new_pos[1]-iboard.pos[1] #路名偏移量
        
        #重设目标路牌坐标
        iboard.reset_pos_xy(new_pos)
        for road in iboard.road_dict.values():
            road.pos = road.pos[0]+dx, road.pos[1]+dy
        
        #重设干扰路牌坐标
        flanker_boards = self.get_flanker_boards()
        for fboard in flanker_boards:
            fboard.reset_pos_xy((fboard.pos[0]+dx, fboard.pos[1]+dy))
            for road in fboard.road_dict.values():
                road.pos = road.pos[0]+dx, road.pos[1]+dy
     
        
class Road(object):
    #name = ''           #路名   
    #pos = 0, 0          #路名中心点在路牌上的位置坐标, 坐标会不断变化
    #is_target = False   #是否是目标路名
    #is_real = False     #是否真名
    
    def __init__(self, name, pos, size=15, is_target=False, is_real=False):
        self.name = name
        self.pos = pos
        self.size = size
        self.is_target = is_target
        self.is_real = is_real

    def __str__(self):
        return u'%s, %s, %s' % (self.name, self.pos, self.is_target)    
    
    def dist_with(self, a_road):
        '''计算路名间距, 结果取2位小数'''
        return maths.dist(self.pos, a_road.pos)
    
    def update_pos(self, target_pos, is_left_algo): #算法规则与路牌同名方法相同, 以后可考虑重构提取公共方法.
        '''根据两点间距变化值, 重新计算当前路名/路牌坐标. 
        根据两点原有坐标可确定间距变化方向, 目标项坐标不变, 干扰项则远离或靠近
        @param target_pos: 目标项位置坐标, 元组对象(x, y)
        @param is_left_algo: 算法参数, 如 True=0.5r, False=r+1
        '''
        
        x0, y0 = target_pos
        x, y = self.pos
        r = maths.dist((x0, y0), (x, y)) #两路名原来的间距
        if is_left_algo:
            r1 = r * SPACING_PARAM['left']
        else:
            r1 = r + SPACING_PARAM['right']
                        
        x = x0 - r1*(x0-x)/r*1.0
        y = y0 - r1*(y0-y)/r*1.0
        self.pos = round(x,2), round(y,2)
        
    def reset_size(self, is_left_algo):
        '''重设路名尺寸'''
        if is_left_algo:
            if self.size*SIZE_PARAM['left'] >= SIZE_BORDER[0]:
                self.size *= SIZE_PARAM['left'] 
            else: 
                self.size = SIZE_BORDER[0]
        else:
            if self.size*SIZE_PARAM['right'] < SIZE_BORDER[1]:
                self.size *= SIZE_PARAM['right']
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
    

