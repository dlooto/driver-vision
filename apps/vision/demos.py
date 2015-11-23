#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#
'''
试验线程类
'''

from vision.models import Demo, Block, Trial
from vision.algos import StepProcess, RstepProcess, NstepProcess, SstepProcess,\
    VstepProcess
from utils import times, eggs, logs
from utils.eggs import float_list_to_str
from config import *
import threading
from vision.trials import Board, WatchPoint


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
    is_update_step_value = False    #是否更新阶梯变量值
    is_left_algo = True             #是否采用左侧算法   
    total_trials = 0                #总刺激显示次数
    total_correct_judge = 0         #总正确判断次数
    
    def __init__(self, gui, param):
        threading.Thread.__init__(self)
        
        self.gui = gui
        self.param = param
        self.wpoint = WatchPoint()
        self.board = self.build_board()
        
    def run(self):
        print('Demo thread started')
        self.is_started = True              #实验进行状态, 默认为未开始
        self.control_demo()
        print('Demo thread ended')
        
    def build_board(self):
        '''需要子类重载'''
        return Board(self.param.eccent, self.param.init_angle)  
    
    def control_demo(self):
        '''控制刺激过程. 阶梯过程包括: 数量阈值, 尺寸阈值, 关键间距, 动态敏感度
        首先以 静态单路牌 为例...
        '''
        
        self.demo = self.save_demo() #以备后用
        road_seats, target_seats = self.param.get_road_seats()
        
        # 关键间距        
        for tseat in target_seats:
            self.board.load_roads(road_seats, tseat, self.param.road_size)
            block_data = {
                'demo':  self.demo, 
                'tseat': tseat, 
                'ee':    self.board.get_ee(tseat, self.wpoint), 
                'angle': self.board.get_angle(tseat, self.wpoint), 
                'cate':  'R', 
                'N':     len(road_seats)-1, 'S': self.param.road_size, 'V': 0.0
            }
            block = self.create_block(block_data)
            
            #for i in range(STEPS_COUNT):
            i = 0
            while self.is_started and i < STEPS_COUNT:
                i += 1    
                self.total_trials += 1
                trial_data = {
                    'block':        block,  
                    'cate':         block.cate, 
                    'steps_value':  float_list_to_str(self.board.get_road_spacings()), 
                    'target_road':  self.board.get_target_road().name
                }
                self.append_trial(trial_data)
                
                self.tmp_begin_time = times.now() #记录刺激显示开始时间
                self.gui.draw_all(self.board, self.wpoint) #刺激显示
                self.wait() #等待用户按键判断
                
                if not self.is_awakened(): #自然等待1.6s, 视为用户判断错误
                    self.current_trial.is_correct = False
                    self.handle_judge(False) 
                
                #用户按键唤醒线程后刷新路名    
                self.board.flash_road_names(road_seats, tseat)
                if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                    continue
                
                # 更新阶梯变量: R
                #self.board.update_flanker_poses(self.is_left_algo)
                self.board.update_flanker_spacings(self.is_left_algo)
                #print 'Spacing changed: ', self.is_left_algo, self.board.get_road_spacings()   #test...
                print 'Poses changed:', self.is_left_algo, self.board.get_road_poses()

        # 数量阈值            
        
        
#         block_querylist = []
#         self.trial_querylist = []    
#         for d in self.target_seats:
#             block = self.create_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
#             NstepProcess(block).execute()
#         Block.objects.bulk_create(block_querylist)
#         Trial.objects.bulk_create(self.trial_querylist) #??             
#              
#         # 尺寸阈值
#         block_querylist = []
#         self.trial_querylist = []  
#         for d in self.target_seats:
#             block = self.create_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
#             SstepProcess(block).execute()
#         Block.objects.bulk_create(block_querylist)
#         Trial.objects.bulk_create(self.trial_querylist) #??              
             
             
        # 动态敏感度            
        #for d in self.target_seats:
        #    block = self.create_block(demo) # (demo, tseat, eccent, angle, cate, N, S, R, V)
        #    VstepProcess(block).execute()
        
        #批量保存block数据
        self.end_demo(is_break=not self.is_started)  #is_started=True则试验未被中断, 否则被中断        
        
    def end_demo(self, is_break=False):
        '''is_break: True-试验被中断, False-试验未被中断. 
        '''
        #print '====================>B'
        #print self.trial_querylist
        #print '====================>E'  
        Trial.objects.bulk_create(self.trial_querylist)
        
        self.demo.time_cost = round(times.time_cost(self.demo.created_time))
        self.demo.correct_rate = round(self.total_correct_judge*1.0/self.total_trials, 2)
        self.demo.is_break = is_break
        self.demo.save()
        
        self.gui.stop()
            
    def handle_judge(self, is_correct):
        '''用户判断后处理, called by key_pressed_method in gui
        @param is_correct:  用户按键判断是否正确.
        is_left_algo: 表示阶梯值新值计算类型, True表示按流程图左侧算法进行计算, 否则按右侧算法.
        is_update_step_value: 是否更新阶梯变量值, 判断成功后该标记值取反, 判断失败后更新阶梯变量值
        
        '''
        if is_correct:
            self.is_update_step_value = not self.is_update_step_value 
            self.is_left_algo = True
        else:
            self.is_update_step_value = True    #需要更新阶梯变量, 以进行下一次刺激显示 
            self.is_left_algo = False           #按右侧方式更新阶梯变量值                
        
    def is_judge_correct(self, is_real=True):
        '''确定用户按键判断是否正确. is_real为用户输入的判断值, 
            True: 用户判断为真路名, 
            False: 用户判断为假路名'''
        if is_real and self.board.is_target_road_real() or not is_real and not self.board.is_target_road_real(): #判断正确
            self.current_trial.is_correct = True
            self.total_correct_judge += 1
        else: #判断错误
            self.current_trial.is_correct = False    
            
        self.current_trial.resp_cost = times.time_cost(self.tmp_begin_time)
        return self.current_trial.is_correct                  
            
    def build_step_process(self):
        return StepProcess()            
    
    def save_demo(self):
        demo = Demo(param=self.param)
        demo.save()
        return demo   
    
    def create_block(self, data): #TODO...
        '''进入阶梯循环过程之前调用该方法, 根据调整后的时间复杂度, 立即save不会影响性能'''
        block = Block(**data)
        block.save()
        return block
    
    def append_trial(self, data): 
        '''暂存trial数据对象'''
        trial = Trial(**data)
        self.trial_querylist.append(trial)
        self.current_trial = trial         #current_trial属性变化是否会影响到最终save DB的值?
        
    def wait(self):
        '''等待1.6s, 以待用户进行键盘操作判断目标路名真/假并唤醒  
        '''
        self.signal.clear()  ##重置线程flag标志位为False, 以使得signal.wait调用有效.                   
        self.signal.wait(show_interval)
        
    def is_awakened(self):
        '''线程是否被用户按键唤醒, 若刺激显示是自然等待1.6s开始下一帧则未被唤醒, 此时返回False. 
        用户按键做判断后, 线程将被唤醒, 唤醒标识位设置为True, '''
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
    
        