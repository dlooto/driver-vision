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


# from django.dispatch.dispatcher import receiver
# from django.dispatch import Signal
# 
# 
# s_start_move = Signal(providing_args=['worker', ])
# s_stop_move = Signal(providing_args=['worker', ])


class MotionWorker(threading.Thread):
    '''运行线程'''
    
    interval = MOVE_SLEEP_TIME
    
    def __init__(self, move_scheme, gui, board, wpoint):
        threading.Thread.__init__(self)
        
        # 运动模式/类型等
        self.move_scheme = move_scheme
        
        # 运动对象: 注视点, 目标项, 干扰项
        self.gui = gui
        self.board = board      #单路牌或多牌路
        self.wpoint = wpoint
        
        self.is_working = False
    
#     def start(self):
#         """路牌开始运动: 发送运动信号, 实现异步处理"""
#         #s_start_move.send(sender=self.__class__, worker=self)
#         start_move.delay(self)
        
    def stop(self):
        """停止运动"""
        self.is_working = False
        
    def run(self):
        self.is_working = True
        
        while self.is_working:
            self.wpoint.move(self.move_scheme)
            self.board.move(self.move_scheme)
            self.gui.draw_all(self.board, self.wpoint)
            time.sleep(self.interval)
            
        #print 'move thread ended'    
        
    def _draw_point(self):  #绘制圆点, for test
        #self.gui.erase_all()
        point = WatchPoint(pos=self.board.pos, radius=1)
        self.gui.draw_wpoint(point)
        self.gui.cv.update()
        
               
class MoveScheme(object):
    
    wp_v = WPOINT_DEFAULT_VELOCITY  #注视点运动时默认速度值
    
    def __init__(self, wp_scheme='S', v=20):
        '''注视点默认为静止
        @param wp_scheme: 注视点模式, S-静止, L-直线运动.
        @param v: 速度值
        '''
        self.wp_grad_x = random.choice(X_DIRECTS)   #x轴变化方向
        self.wp_grad_y = random.choice(GRADS)       #y轴变化方向斜率值
        
        self.wp_scheme = wp_scheme
        self.v = v                      #速度值: 角速度值或直线速率值
        
    def print_wp_direct(self):   
        print '注视点运动方向: (wp_grad_x, wp_grad_y): (%s, %s)' % (self.wp_grad_x, self.wp_grad_y)
        
    def print_direct(self):
        self.print_wp_direct()
        
    def line_formula(self, old_pos, dx, kx, ky):
        '''直线公式: 
            x=x0 + kx*dx, 其中 dx=v*t(v为运动速度值)
            y=y0 + ky*dx
        
        @param old_pos: 移动前坐标值(x,y)
        @return: 新坐标(x,y)
        '''
        return old_pos[0] + kx*dx, old_pos[1] + ky*dx
        
    def new_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''由路牌原坐标计算移动后的新坐标'''
        pass    
        
    def new_wp_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''注视点移动后的新坐标计算
        x=k*X0+A中, k决定了直线的方向 
        '''
        if self.is_wpoint_move():
            dx = self.wp_v * t
            return self.line_formula(old_pos, dx, self.wp_grad_x, self.wp_grad_y)
        return old_pos     
        
    def set_velocity(self, v):
        self.v = v
        
    def is_wpoint_move(self):
        '''注视点是否运动'''
        return True if self.wp_scheme == 'L' else False
        
class CircleMoveScheme(MoveScheme):
    '''圆周运动'''
    
    def __init__(self, center_pos, wp_scheme='S', v=None):
        MoveScheme.__init__(self, wp_scheme, v)
        self.center_pos = center_pos
    
    def new_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''
        @param old_pos:    移动目标中心点的原始坐标
        @param center_pos: 所围绕的圆心点坐标
        @param t:          旋转的时间间隔(v*t为角度值)
        '''
        xe, ye = self.center_pos[0], self.center_pos[1]
        x0, y0 = old_pos[0], old_pos[1]
        dx, dy = xe-x0, ye-y0  
        rad_a = math.radians(self.v*t)
        sin, cos = math.sin(rad_a), math.cos(rad_a)
        return xe-cos*dx+sin*dy, ye-sin*dx-cos*dy
        

class SmoothMoveScheme(MoveScheme):
    '''平滑运动'''

    def __init__(self, wp_scheme='S'):
        MoveScheme.__init__(self, wp_scheme)
        self.grad_x = random.choice(X_DIRECTS)   #x轴变化方向
        self.grad_y = random.choice(GRADS)       #y轴变化方向斜率值
        
    def new_pos(self, old_pos, t=MOVE_SLEEP_TIME):
        '''计算平滑运动新坐标'''
        dx = self.v * t
        return self.line_formula(old_pos, dx, self.grad_x, self.grad_y)
        
    def print_direct(self):
        self.print_wp_direct()
        print '平滑运动方向: (grad_x, grad_y): (%s, %s)' % (self.grad_x, self.grad_y)

class MixedMoveScheme(MoveScheme):
    '''混合运动'''
    pass

    

        
                
        
        