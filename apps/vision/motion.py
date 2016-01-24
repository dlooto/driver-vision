#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Jan 3, 2016, by Junn
#

'''
运动及速度相关
'''

import time
import random
import threading
from vision.config import *
from vision.trials import WatchPoint
# from vision.tasks import start_move


class MotionWorker(threading.Thread):
    '''运行线程'''
    
    interval = MOVE_SLEEP_TIME
    
    def __init__(self, gui, board, wpoint):
        threading.Thread.__init__(self)
        
        # 运动对象: 注视点, 目标项, 干扰项
        self.gui = gui
        self.board = board      #单路牌或多牌路
        self.wpoint = wpoint
        
        self.is_working = False
    
    def stop(self):
        """停止运动"""
        self.is_working = False
        
    def run(self):
        self.is_working = True
        
        while self.is_working:
            self.board.glue_with(self.wpoint) #判断并处理粘附
            
            self.wpoint.move()
            self.board.move()
            self.gui.draw_all(self.board, self.wpoint)
            time.sleep(self.interval)
        #print 'move thread ended'    
        
    def _draw_point(self):  #绘制圆点, for test
        #self.gui.erase_all()
        point = WatchPoint(pos=self.board.pos, radius=1)
        self.gui.draw_wpoint(point)
        self.gui.cv.update()
        
               
class MoveScheme(object):
    
    def __init__(self, v):
        '''注视点默认为静止'''
        
        #速度值, 角速度值或直线速率值
        self.v = v 
        
    def is_move(self):
        '''是否运动. 静态过程直接返回False'''
        return True        
        
    def new_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''由物体移动后的新坐标'''
        return old_pos    
        
    def random_direction(self):
        '''随机改变到另一个方向'''
        pass      
    
    def get_direction(self):
        '''获取当前方向值'''
        pass  
    
    def change_to(self):
        pass
    
    def reverse_direction(self):
        '''平滑运动时方向反转'''
        pass    
        
    def set_velocity(self, v):
        self.v = v
        
    def get_velocity(self):
        return self.v    
    
    def copy_fields(self, move_scheme):
        pass
    
    def print_direction(self):
        pass
    
    def scheme_type(self): #for testing
        print type(self)    
        
        
class DefaultMoveScheme(MoveScheme):
    '''默认静态模式(非运动模式). Do nothing when moving'''
    
    def is_move(self):
        return False 
    
    def get_velocity(self):
        return 0       
        

class CircleMoveScheme(MoveScheme):
    '''圆周运动'''
    
    def __init__(self, center_pos, v=BOARD_DEFAULT_VELOCITY):
        MoveScheme.__init__(self, v)
        self.center_pos = center_pos            #圆心坐标
    
    def new_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''
        @param old_pos:    移动目标中心点的原始坐标
        @param t:          旋转的时间间隔(由此计算出角度值 v*t )
        '''
        xe, ye = self.center_pos[0], self.center_pos[1]
        x0, y0 = old_pos[0], old_pos[1]
        dx, dy = xe-x0, ye-y0  
        rad_a = math.radians(self.v*t)
        sin, cos = math.sin(rad_a), math.cos(rad_a)
        return xe-cos*dx+sin*dy, ye-sin*dx-cos*dy
        

class SmoothMoveScheme(MoveScheme):
    '''平滑运动, 即直线运动'''
    
    #设定水平及垂直正方向: 左右上下
    DIRECTIONS = {      
        'left':  (-1, 0),  #(grad_x, grad_y)
        'right': (1, 0),   
        'up':    (0, -1),
        'down':  (0, 1),  
    }
    
    def __init__(self, v=BOARD_DEFAULT_VELOCITY):
        MoveScheme.__init__(self, v)
        self.grad_x = random.choice(X_DIRECTS)   #x轴变化方向
        self.grad_y = random.choice(GRADS)       #y轴变化方向斜率值
        
    def copy_fields(self, move_scheme):
        '''参数拷贝, 用于处于粘附问题'''
        self.v = move_scheme.v
        self.grad_x = move_scheme.grad_x
        self.grad_y = move_scheme.grad_y    
        
    def _line_formula(self, old_pos, dx, grad_x, grad_y):
        '''直线公式: 
            x=x0 + grad_x*dx, 其中 dx=v*t(v为运动速度值)
            y=y0 + ky*dx
        
        @param old_pos: 移动前坐标值(x,y)
        @param dx:      x轴偏移量
        @param grad_x:  x轴变化率
        @param grad_y:  y轴变化率
        
        @return: 新坐标(x,y)
        '''
        return old_pos[0] + grad_x*dx, old_pos[1] + grad_y*dx        
        
    def new_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''计算平滑运动新坐标'''
        return self._line_formula(old_pos, self.v*t, self.grad_x, self.grad_y)
    
    def get_direction(self):
        '''动态敏感度阈值过程时用到该方法'''
        if self.is_up():    #上
            return 1
        if self.is_down():  #下
            return 2
        if self.is_left():  #左 
            return 3
        if self.is_right(): #右
            return 4
        return -1       #Unkonw direction
        
    def random_direction(self):
        '''运动敏感度阈值过程时: 改变下一帧的运动方向, 在'上下左右'4个垂直方向中随机选择'''
        label = random.choice(self.DIRECTIONS.keys())
        self.change_to(label)
        
    def change_to(self, label):
        '''改变到指定运动方向, 适用于动态敏感度阈值.
        @param label: 方向标识, 取值范围为 ('left', 'right', 'up', 'down') 
        '''
        direction = self.DIRECTIONS[label]
        self.grad_x, self.grad_y = direction[0], direction[1]
        print 'Direction changed to: %s' % label
        
    def reverse_direction(self):
        '''朝相反方向运动. 仅限于平滑运动'''
        self.grad_x, self.grad_y = -self.grad_x, -self.grad_y
        print 'Changed to reversed direction: (%s, %s)' % (self.grad_x, self.grad_y)
        
#     def reverse_direction(self):
#         '''运动敏感度阈值过程时, 且路牌越过边界时则向反方向运动'''
#         if self.is_up(): #上
#             self.change_to(self.DIRECTIONS['down'], 'down')
#             return
#         if self.down(): #下
#             self.change_to(self.DIRECTIONS['up'], 'up')
#             return
#         if self.is_left(): #左 
#             self.change_to(self.DIRECTIONS['right'], 'right')
#             return
#         if self.is_right(): #右
#             self.change_to(self.DIRECTIONS['left'], 'left')
#             return
        
    def is_up(self):
        return self.grad_x == 0 and self.grad_y == -1 #上

    def is_down(self):
        return self.grad_x == 0 and self.grad_y == 1 #下
    
    def is_left(self):
        return self.grad_x == -1 and self.grad_y == 0 #左
    
    def is_right(self):
        return self.grad_x == 1 and self.grad_y == 0 #右
    
    def print_direction(self):
        print '平滑运动方向 (grad_x, grad_y): (%s, %s)' % (self.grad_x, self.grad_y)

class MixedMoveScheme(MoveScheme):
    '''混合运动'''
    pass

    

        
                
        
        