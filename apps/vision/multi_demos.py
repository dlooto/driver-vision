#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#

from config import *
from utils import times
from vision.trials import  MultiBoard
from vision.demos import DemoThread

'''
多路牌试验线程类
'''
    
class MultiDemoThread(DemoThread):
    '''多路牌试验线程基类'''

    def build_board(self):
        return MultiBoard(self.param)
    
    def step_process(self, param, step_algo):
        '''阶梯过程. 不同阶梯过程差异使用多态解决. 默认静态试验
            @override 重写父类方法
        '''
        
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        
        step_algo.print_prompt()
        
        for bkey in self.board.board_repos.keys():   #====路牌循环, 各路牌轮询作为目标路牌
            if not self.is_started: break
            self.board.set_target_board(bkey)
            
            for tseat in self.board.get_spared_target_seats(bkey): #====目标路名循环(在当前目标路牌上的)
                if not self.is_started: break
                
                self.prompt_target_multi(bkey, tseat)
                for velocity in param.get_velocitys():
                    if not self.is_started: break
                    
                    step_algo.set_velocity(velocity)    #extend_block_data时需要V参数
                    
                    for eccent in eccent_list:   #====离心率循环
                        for angle in angle_list: #====角度循环     
                            step_algo.init_boards()
                            
                            # 每一轮更新离心率和角度值, 都需要重设路牌坐标并加载路名
                            self.board.reset_boards(eccent, angle)
                            self.board.load_roads(bkey, tseat)
                            
                            # Save Block data
                            block_data = {
                                'demo':  self.demo, 
                                'tseat': '%s:%s' % (bkey, tseat),   #目标项- 路牌key:目标路名seat
                                'ee':    self.board.calc_ee(self.wpoint),   
                                'angle': self.board.calc_angle(self.wpoint),
                            }
                            step_algo.extend_block_data(block_data)
                            block = self.create_block(block_data)
                            print 'Block: ', block_data
                            
                            # 阶梯变化开始
                            self.deglue() #阶梯过程前去除粘附
                            
                            step_algo.prepare_steping()
                            for i in range(STEPS_COUNT):
                                if not self.is_started: break
                                
                                # Append Trial data
                                self.total_trials += 1
                                trial_data = {
                                    'block':        block,  
                                    'cate':         block.cate,
                                    'steps_value':  step_algo.get_steps_value(),    #TODO---
                                    'target_road':  self.board.get_target_name(),  
                                    'move_direct':  str(self.board.get_move_direction()),
                                    'wp_velocity':  self.wpoint.get_move_velocity(), 
                                    'created_time': times.now()
                                }
                                self.current_trial = self.append_trial(trial_data)
                                
                                #刺激显示一帧并进入按键等待. 若为动态模式则开始运动线程.
                                self.show_frame()
                                
                                if not self.is_awakened(): #非被唤醒并自然等待1.6s, 视为用户判断错误
                                    self.current_trial.is_correct = False
                                    self.handle_judge(is_correct=False)
                                
                                # 线程唤醒后刷新路名
                                step_algo.flash_contents()
                                if not self.is_update_step_value: #不更新阶梯变量, 则直接进行第2次刺激显示
                                    continue
                                
                                # 更新阶梯变量
                                step_algo.update_vars(self.is_left_algo) #TODO---
                

class StaticMultiDemoThread(MultiDemoThread):
    '''静态多路牌'''
    
    def label(self):
        return u'静态多路牌试验'    
    
    def step_process(self, param, step_algo):
        ''' 阶梯过程 '''
        super(StaticMultiDemoThread, self).step_process(param, step_algo) 
        
    #### 静态模式重写以下方法为空  
    def start_motion_worker(self): 
        pass                   
    
    def stop_motion_worker(self):
        pass    
    
    def build_velocity_step_algo(self, board, wpoint): #多态重写
        raise Exception(u'静态模式无动态敏感度阈值阶梯过程')
            
    
class DynamicMultiDemoThread(MultiDemoThread):
    '''动态多路牌'''
    
    def label(self):
        return u'动态多路牌试验'        
    
    def step_process(self, param, step_algo):
        '''overwrite'''
        super(DynamicMultiDemoThread, self).step_process(param, step_algo)
    
    # 动态敏感度
    
    
    


    
        