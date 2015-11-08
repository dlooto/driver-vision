#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#
from vision.models import Demo, Block
from vision.algos import StepProcess, RstepProcess, NstepProcess, SstepProcess,\
    VstepProcess

'''
试验线程类
'''

from config import *
import threading
from vision.trials import Board, WatchPoint

  
class DemoThread(threading.Thread):
    '''父类试验线程对象. 
    '''
    is_started = False              #实验进行状态, 默认为未开始
    signal = threading.Event()
    
    param = None      #数据库读取的参数对象  
    wpoint = None     #注视点
    board = None      #多路牌时为Board对象列表结构, 单路牌时为Board对象结构    
    
    def __init__(self, gui, param):
        threading.Thread.__init__(self)
        
        self.gui = gui
        self.param = param
        self.wpoint = WatchPoint()
        self.board = self.build_board()

    def run(self):
        print('Demo thread started')
        self.is_started = True              #实验进行状态, 默认为未开始
        self.control_trials()
        
    def build_board(self):
        '''需要子类重载'''
        return Board()  
    
    def control_trials(self):
        '''控制刺激过程
        阶梯过程: 数量阈值, 尺寸阈值, 关键间距, 动态敏感度
        '''
        
        demo = self.save_demo()

        # 关键间距        
        for d in self.target_seats:
            block = self.cache_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
            RstepProcess(block).execute()
            
        # 数量阈值            
        for d in self.target_seats:
            block = self.cache_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
            NstepProcess(block).execute()
            
        # 尺寸阈值            
        for d in self.target_seats:
            block = self.cache_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
            SstepProcess(block).execute()
            
        # 动态敏感度            
        for d in self.target_seats:
            block = self.cache_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
            VstepProcess(block).execute()
                                    
            
    def build_step_process(self):
        return StepProcess()            
    
    def save_demo(self):
        demo = Demo(param=self.param)
        demo.save()
        return demo   
    
    def cache_block(self): #TODO...
        '''进入阶梯循环过程之前调用该方法'''
        block = Block()
        return block                          
        
#     def next_trial(self, ):
#         '''每一次刺激试验为1.6s. 该方法在单独的线程中被循环调用'''
#         # 刷新控制参数, 为下一次1.6s的刺激显示作准备
#         self.board.change_params()         
#         self.gui.draw(self.board)
#         self.wait()
        
    #重置线程flag标志位为False, 以使得signal.wait调用有效.   
    #等待1.6s, 以待用户进行键盘操作 y/n 并唤醒  
    def wait(self):
        self.signal.clear()                   
        self.signal.wait(show_interval)   
        
    def awake(self):
        self.signal.set()  
        
        
class StaticSingleDemoThread(DemoThread):
    '''静态单路牌'''
    
    pass

class StaticMultiDemoThread(DemoThread):
    '''静态多路牌'''
    
    def build_board(self):
        #TODO... build multi boards
        return Board()
    
class DynamicSingleDemoThread(DemoThread):
    '''动态单路牌'''
    pass

class DynamicMultiDemoThread(DemoThread):
    '''动态多路牌'''
    pass
    
        