#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#

import time
from vision.models import Demo, Block, Trial
from utils import times, eggs, logs
from utils.eggs import float_list_to_str
from config import *
import threading
from vision.trials import Board, WatchPoint
from vision.algos import SpaceStepAlgo, NumberStepAlgo, SizeStepAlgo,\
    VelocityStepAlgo

'''
试验线程类
'''

class DemoThread(threading.Thread):
    '''父类试验线程对象.  为初始参数, 路牌,注视点等的容器
    '''
    is_started = False              #实验进行状态, 默认为未开始
    signal = threading.Event()
    
    param = None      #数据库读取的参数对象  
    wpoint = None     #注视点
    board = None      #多路牌时为Board对象列表结构, 单路牌时为Board对象结构
    
    #辅助结构
    demo = None
    trial_querylist = []            #缓存trial model对象, 用于批量存储数据
    is_update_step_value = True     #是否更新阶梯变量值, 默认更新阶梯变量(很重要)
    is_left_algo = True             #是否采用左侧算法   
    total_trials = 0                #总刺激显示次数
    total_correct_judge = 0         #总正确判断次数
    
    def __init__(self, gui, param):
        threading.Thread.__init__(self)
        
        self.gui = gui
        self.param = param
        self.wpoint = WatchPoint()
        self.board = self.build_board(param)
        
    def run(self):
        print('Demo thread started')
        
        self.is_started = True          #实验进行状态, 默认为未开始
        self.new_demo()                 #以备后用
        self.step_process(self.param)
        
        #批量保存block数据, is_started=True则试验未被中断, 否则被中断
        self.end_demo(is_break=not self.is_started)
        
        print('Demo thread ended')
        
    def build_board(self, param):
        '''需要子类重载'''
        #return Board(self.param.eccent, self.param.init_angle, width=width, height=height)
        width, height = self.param.get_board_size()
        return Board(self.param.road_size, width=width, height=height)
    
    def control_demo(self):
        '''控制刺激过程. 阶梯过程包括: 数量阈值, 尺寸阈值, 关键间距, 动态敏感度
        首先以 静态单路牌 为例...
        '''
        
        self.new_demo(self.param) #以备后用
        self.step_process(self.param)
        
        #批量保存block数据
        self.end_demo(is_break=not self.is_started)  #is_started=True则试验未被中断, 否则被中断        

    def prompt_target_seat(self, target_seat):
        '''绘制目标位置提示, 停留3秒'''
        self.gui.draw_target_seat(target_seat, self.board)
        time.sleep(TARGET_SEAT_PROMPT['interval'])

    def critical_spacing(self, param):
        road_seats, target_seats = param.get_road_seats()
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        width, height = param.get_board_size()
        
        print('\n求关键间距控制过程开始...')
        
        for tseat in target_seats:
            if not self.is_started: break
            
            self.prompt_target_seat(tseat)
            for eccent in eccent_list:
                for angle in angle_list:
                    self.board.reset_pos(eccent, angle, width=width, height=height)
                    self.board.load_roads(road_seats, tseat, param.road_size)
                    block_data = {
                        'demo':  self.demo, 
                        'tseat': tseat, 
                        'ee':    self.board.get_ee(tseat, self.wpoint), 
                        'angle': self.board.get_angle(tseat, self.wpoint), 
                        'cate':  'R', 
                        'N':     len(road_seats)-1, 'S': param.road_size, 'V': 0.0
                    }
                    block = self.create_block(block_data)
                    print 'Block: ', block_data
                    
                    for i in range(STEPS_COUNT):
                        if not self.is_started: break
                        self.total_trials += 1
                        trial_data = {
                            'block':        block,  
                            'cate':         block.cate, 
                            'steps_value':  self.get_steps_value(), 
                            'target_road':  self.board.get_target_road().name,
                            'created_time': times.now()
                        }
                        self.current_trial = self.append_trial(trial_data)
                        
                        self.gui.draw_all(self.board, self.wpoint) #刺激显示
                        self.wait() #等待用户按键判断
                        
                        if not self.is_awakened(): #自然等待1.6s, 视为用户判断错误
                            self.current_trial.is_correct = False
                            self.handle_judge(is_correct=False)
                        
                        #用户按键唤醒线程后刷新路名    
                        self.board.flash_road_names(road_seats, tseat)
                        if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                            continue
                        
                        # 更新阶梯变量: R
                        self.board.update_flanker_spacings(self.is_left_algo)
                        print 'Spacing changed: ', '0.5r' if self.is_left_algo else 'r+1', self.board.get_road_spacings()   #test...
                        #print 'Poses changed:', self.is_left_algo, self.board.get_road_poses()            

    def number_threshold(self, param):
        '''求数量阈值过程. 干扰项数量进行阶梯变化--增加或减少
        @param road_seats: 路名位置列表, 如['A', 'B', 'G', 'E']
        @param target_seats: 可选的目标位置列表, 如['A', 'B', 'E']
        '''
        road_seats, target_seats = param.get_road_seats()
        width, height = param.get_board_size()
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        
        print('\n求数量阈值控制过程开始...')
        
        for tseat in target_seats:
            if not self.is_started: break
            
            self.prompt_target_seat(tseat)
            for eccent in eccent_list:
                for angle in angle_list:            
                    self.board.reset_pos(eccent, angle, width=width, height=height)
                    self.board.load_roads(road_seats, tseat, param.road_size)  #重新加载路名对象
                    block_data = {
                        'demo':  self.demo, 
                        'tseat': tseat, 
                        'ee':    self.board.get_ee(tseat, self.wpoint), 
                        'angle': self.board.get_angle(tseat, self.wpoint), 
                        
                        'cate':  'N', #求数量阈值
                        'S': param.road_size, 'V': 0.0   # 'R': 应该为空, 因间距个数不确定
                    }
                    block = self.create_block(block_data)
                    print 'Block: ', block_data
                    
                    # 阶梯变化开始
                    dynamic_road_seats = road_seats[:]  #拷贝路名位置
                    self.board.clear_queue() #清空辅助队列, 用于干扰路名增减
                    for i in range(STEPS_COUNT):
                        if not self.is_started: break  
                        self.total_trials += 1
                        trial_data = {
                            'block':        block,  
                            'cate':         block.cate, 
                            'steps_value':  len(self.board.get_flanker_roads()),  #Changed.
                            'target_road':  self.board.get_target_road().name,
                            'created_time': times.now()
                        }
                        self.current_trial = self.append_trial(trial_data)
                        
                        self.gui.draw_all(self.board, self.wpoint) #刺激显示
                        self.wait() #等待用户按键判断
                        
                        if not self.is_awakened(): #非被唤醒并自然等待1.6s, 视为用户判断错误
                            self.current_trial.is_correct = False
                            self.handle_judge(is_correct=False)
                        
                        #用户按键唤醒线程后刷新路名    
                        self.board.flash_road_names(dynamic_road_seats, tseat) #TODO: 是否
                        if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                            continue
                        
                        # 更新阶梯变量   #Changed.
                        dynamic_road_seats = self.board.update_flanker_numbers(self.is_left_algo, param.road_size)
                        print 'Flankers:', 'N+2' if self.is_left_algo else 'N-1', len(self.board.get_flanker_roads())            
        
    def size_threshold(self, param): 
        '''求尺寸阈值过程. 干扰项与目标项尺寸一同变化
        '''
        road_seats, target_seats = param.get_road_seats()
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        width, height = param.get_board_size()
        
        print('\n求尺寸阈值过程开始...')
        
        for tseat in target_seats:
            if not self.is_started: break
            
            self.prompt_target_seat(tseat)
            for eccent in eccent_list:
                for angle in angle_list:         
                    self.board.reset_pos(eccent, angle, width=width, height=height)   
                    self.board.load_roads(road_seats, tseat, param.road_size)  #加载路名
                    block_data = {
                        'demo':  self.demo, 
                        'tseat': tseat, 
                        'ee':    self.board.get_ee(tseat, self.wpoint), 
                        'angle': self.board.get_angle(tseat, self.wpoint), 
                        
                        # Changed
                        'cate':  'S', #求尺寸阈值
                        'N': len(road_seats)-1, 'V': 0.0   # 'R': 置空, 间距随路名尺寸变化而变化
                    }
                    block = self.create_block(block_data)
                    print 'Block: ', block_data
                    
                    # 阶梯变化开始
                    for i in range(STEPS_COUNT):
                        if not self.is_started: break
                        self.total_trials += 1
                        trial_data = {
                            'block':        block,  
                            'cate':         block.cate, 
                            'steps_value':  self.board.get_road_size(),  #Changed.
                            'target_road':  self.board.get_target_road().name, 
                            'created_time': times.now()
                        }
                        self.current_trial = self.append_trial(trial_data)
                        
                        self.gui.draw_all(self.board, self.wpoint) #刺激显示
                        self.wait() #等待用户按键判断
                        
                        if not self.is_awakened(): #非被唤醒并自然等待1.6s, 视为用户判断错误
                            self.current_trial.is_correct = False
                            self.handle_judge(is_correct=False)
                        
                        #用户按键唤醒线程后刷新路名    
                        self.board.flash_road_names(road_seats, tseat)
                        if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                            continue
                        
                        # 更新阶梯变量   #Changed.
                        self.board.update_road_size(self.is_left_algo)
                        print 'Road size:', '*1.2' if self.is_left_algo else '*0.8', self.board.get_road_size()                       
        
    def dynamic_sensitive(self, road_seats, target_seats):
        pass    
    
    def step_process(self, param):
        '''阶梯过程. 重构后使用该统一代码流程, 不同阶梯过程差异使用多态解决
        '''
        
        if param.step_scheme not in ('R', 'S', 'N', 'V'):
            raise Exception('Unknown step scheme: %s' % param.step_scheme)
         
        step_algo = None          
        if param.step_scheme == 'R':        
            step_algo = SpaceStepAlgo(self.board)
        elif param.step_scheme == 'N':    
            step_algo = NumberStepAlgo(self.board)
        elif param.step_scheme == 'S':
            step_algo = SizeStepAlgo(self.board)
        else:
            step_algo = VelocityStepAlgo(self.board)    #动态敏感度
        
        # init params
        road_seats, target_seats = param.get_road_seats()
        width, height = param.get_board_size()
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        
        step_algo.print_prompt()
        for tseat in target_seats:
            if not self.is_started: break
            
            self.prompt_target_seat(tseat)
            for eccent in eccent_list:
                for angle in angle_list:            
                    self.board.reset_pos(eccent, angle, width=width, height=height)
                    self.board.load_roads(road_seats, tseat, param.road_size)  #重新加载路名对象
                    block_data = {
                        'demo':  self.demo, 
                        'tseat': tseat, 
                        'ee':    self.board.get_ee(tseat, self.wpoint), 
                        'angle': self.board.get_angle(tseat, self.wpoint), 
                    }
                    step_algo.extend_block_data(block_data)
                    block = self.create_block(block_data)
                    print 'Block: ', block_data
                    
                    # 阶梯变化开始
                    step_algo.prepare_steping()
                    for i in range(STEPS_COUNT):
                        if not self.is_started: break  
                        self.total_trials += 1
                        trial_data = {
                            'block':        block,  
                            'cate':         block.cate, 
                            'steps_value':  step_algo.get_steps_value(),
                            'target_road':  self.board.get_target_road().name,
                            'created_time': times.now()
                        }
                        self.current_trial = self.append_trial(trial_data)
                        
                        self.gui.draw_all(self.board, self.wpoint) #刺激显示
                        self.wait() #等待用户按键判断
                        
                        if not self.is_awakened(): #非被唤醒并自然等待1.6s, 视为用户判断错误
                            self.current_trial.is_correct = False
                            self.handle_judge(is_correct=False)
                        
                        #用户按键唤醒线程后刷新路名    
                        self.board.flash_road_names() 
                        if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                            continue
                        
                        # 更新阶梯变量
                        step_algo.update_vars(self.is_left_algo)
                              
        
    def get_steps_value(self): #阈值具体的方法, 考虑重载
        return float_list_to_str(self.board.get_road_spacings())
        
    def end_demo(self, is_break=False):
        '''is_break: True-试验被中断, False-试验未被中断. 
        '''
        Trial.objects.bulk_create(self.trial_querylist)
        
        self.demo.time_cost = round(times.time_cost(self.demo.created_time), 1)
        self.demo.correct_rate = round(self.total_correct_judge*1.0/self.total_trials, 2)
        self.demo.is_break = is_break
        self.demo.save()
        
        self.gui.stop()
            
    def handle_judge(self, is_correct):
        '''用户判断后处理, called by key_pressed_method in gui
        @param is_correct:  用户按键判断是否正确, True-判断正确, False-判断错误
        
        is_left_algo: 表示阶梯值新值计算类型, True表示按流程图左侧算法进行计算, 否则按右侧算法.
        is_update_step_value: 是否更新阶梯变量值, 判断成功后该标记值取反, 判断失败后更新阶梯变量值
        
        '''
        if is_correct:
            self.is_update_step_value = not self.is_update_step_value 
            self.is_left_algo = True
        else:
            self.is_update_step_value = True    #需要更新阶梯变量, 以进行下一次刺激显示 
            self.is_left_algo = False           #按右侧方式更新阶梯变量值                
        
    def is_judge_correct(self, is_real):
        '''确定用户按键判断是否正确. 若用户的判断值与路名真实值匹配, 则返回True, 否则返回False
        @param is_real: 为用户输入的判断值, True: 用户判断为真路名, False: 用户判断为假路名
        '''
        if is_real and self.board.is_target_road_real() or not is_real and not self.board.is_target_road_real(): #判断正确
            self.current_trial.is_correct = True
            self.total_correct_judge += 1
        else: #判断错误
            self.current_trial.is_correct = False
            
        self.current_trial.resp_cost = times.time_cost(self.current_trial.created_time)
        return self.current_trial.is_correct                  
            
    def new_demo(self):
        demo = Demo(param=self.param)
        demo.save()
        self.demo =  demo   
    
    def create_block(self, data): 
        '''进入阶梯循环过程之前调用该方法, 根据调整后的时间复杂度, 立即save不会影响性能'''
        block = Block(**data)
        block.save()
        return block
    
    def append_trial(self, data): 
        '''暂存trial数据对象'''
        trial = Trial(**data)
        self.trial_querylist.append(trial)
        return trial
        
    def wait(self):
        '''等待1.6s, 以待用户进行键盘操作判断目标路名真/假并唤醒  
        '''
        self.signal.clear()  ##重置线程flag标志位为False, 以使得signal.wait调用有效.                   
        self.signal.wait(show_interval)
        
    def is_awakened(self):
        '''线程是否被用户按键唤醒, 若刺激显示是自然等待1.6s开始下一帧则未被唤醒, 此时返回False. 
        用户按键做判断后, 线程将被唤醒, 唤醒标识位设置为True, 
        '''
        return self.signal.is_set()           
        
    def awake(self):
        '''唤醒线程. Set the internal flag to true'''
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
    
        