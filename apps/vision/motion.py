#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Jan 3, 2016, by Junn
#
import time
# from vision.tasks import start_move
import threading
'''运动及速度相关'''


# from django.dispatch.dispatcher import receiver
# from django.dispatch import Signal
# 
# 
# s_start_move = Signal(providing_args=['worker', ])
# s_stop_move = Signal(providing_args=['worker', ])


class Velocity(object):
    
    def __init__(self):
        v = 0
        direct = None
        
class MotionWorker(threading.Thread):
    
    def __init__(self, param, board, wpoint):
        threading.Thread.__init__(self)
        
        # 决定运动模式/类型等
        self.param = param
        
        # 运动对象: 注视点, 目标项, 干扰项
        self.board = board  #单路或多路
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
        print 'move started'
        
        while self.is_working:
            print 'In start move...'
            #self.board.move()
            #self.board.redraw() 
            time.sleep(1)
            
        print 'move ended'    
                        
    

        
                
        
        