#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#

from utils import times, eggs, logs
from config import *
import threading
from vision.trials import Board, WatchPoint, MultiBoard
from vision.algos import SpaceStepAlgo, NumberStepAlgo, SizeStepAlgo,\
    VelocityStepAlgo
from vision.demos import DemoThread

'''
多路牌试验线程类
'''
    
class MultiDemoThread(DemoThread):
    '''多路牌试验线程'''

    def build_board(self):
        return MultiBoard(self.param)
    
    def step_process(self, param, step_algo):
        '''阶梯过程. 不同阶梯过程差异使用多态解决. 默认静态试验
            @override 重写父类方法
        '''
        
        #road_seats_list = param.get_multi_road_seats()
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        
        step_algo.print_prompt()
        
        for bkey, iboard in self.board.board_dict.items():    #====路牌循环, 各路牌轮询作为目标路牌
            if not self.is_started: break
            self.board.set_target_board(bkey)
            
            for tseat in iboard.spared_target_seats:         #====目标路名循环
                if not self.is_started: break
                
                self.prompt_target_multi(bkey, tseat)
                for eccent in eccent_list:                  #====离心率循环
                    for angle in angle_list:                #====角度循环     
                        self.board.reset_boards(eccent, angle)
                        self.board.load_roads(bkey, tseat)
                        
                        # Save Block data
                        block_data = {
                            'demo':  self.demo, 
                            'tseat': '%s:%s' % (bkey, tseat),   #目标项- 路牌key:目标路名seat
                            'ee':    self.board.calc_ee(iboard, self.wpoint),   
                            'angle': self.board.calc_angle(iboard, self.wpoint),
                        }
                        step_algo.extend_block_data(block_data)
                        block = self.create_block(block_data)
                        print 'Block: ', block_data
                        
                        # 阶梯变化开始
                        step_algo.prepare_steping()                 #TODO----
                        for i in range(STEPS_COUNT):
                            if not self.is_started: break  
                            
                            # Append Trial data
                            self.total_trials += 1
                            trial_data = {
                                'block':        block,  
                                'cate':         block.cate, 
                                'steps_value':  step_algo.get_steps_value(),    #TODO---
                                'target_road':  self.board.get_target_name(),   
                                'created_time': times.now()
                            }
                            self.current_trial = self.append_trial(trial_data)
                            
                            #刺激显示
                            self.gui.draw_all(self.board, self.wpoint)
                            self.wait() #等待用户按键判断
                            
                            if not self.is_awakened(): #非被唤醒并自然等待1.6s, 视为用户判断错误
                                self.current_trial.is_correct = False
                                self.handle_judge(is_correct=False)
                            
                            #用户按键唤醒线程后刷新路名    
                            self.board.flash_road_names()
                            if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                                continue
                            
                            # 更新阶梯变量
                            step_algo.update_vars(self.is_left_algo)    #TODO---
                
            
    
class DynamicMultiDemoThread(MultiDemoThread):
    '''动态多路牌'''
    
    def str(self):
        return u'动态多路牌试验'        
    
    def step_process(self, param, step_algo): #TODO...
        '''
        @todo: 加入运动过程...
        '''
        super(DynamicMultiDemoThread, self).step_process(param, step_algo)
    
    
class StaticMultiDemoThread(MultiDemoThread):
    '''静态多路牌'''
    
    def str(self):
        return u'静态多路牌试验'    
    

    
        