#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#
from vision.models import Demo, Block, Trial
from vision.algos import StepProcess, RstepProcess, NstepProcess, SstepProcess,\
    VstepProcess

'''
试验线程类
'''

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
        #return Board(self.param.eccent, self.param.init_angle, self.wpoint.pos)
        return Board()  
    
    def control_trials(self):
        '''控制刺激过程
        阶梯过程包括: 数量阈值, 尺寸阈值, 关键间距, 动态敏感度
        ## 首先以 静态单路牌 为例...
        '''
        
        demo = self.save_demo() #以备后用
        road_seats, target_seats = self.param.get_road_seats()
        block_querylist = [] #缓存block对象, 用于批量插入DB   
        trial_querylist = [] #同上
        
        # 关键间距        
        for tseat in target_seats:
            block_data = {
                'demo': demo, 'tseat': tseat, 
                'ee': self.board.get_ee(tseat, self.wpoint), 
                'angle': self.board.get_angle(tseat, self.wpoint), 
                'cate': 'R', 'N': len(road_seats)-1, 'S': self.param.road_size, 'V': 0.0
            }
            block = self.create_block(**block_data)
            block_querylist.append(block)
            self.board.load_roads(road_seats, tseat, self.param.road_size)
            for i in range(STEPS_COUNT):
                self.gui.draw_all(self.board, self.wpoint) #刺激显示
                self.wait() #等待用户按键判断
                
                #用户按键唤醒线程后刷新路名    
                self.board.load_roads(road_seats, tseat, self.param.road_size) 
                if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                    continue
                
                # 更新阶梯变量: R
                self.board.update_flanker_poses(self.is_left_algo)
                
        #批量保存block数据                            
        Block.objects.bulk_create(block_querylist)
        Trial.objects.bulk_create(self.trial_querylist) #?? 
        
#         # 数量阈值            
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
        

            
    def handle_success(self):
        '''处理用户判断成功, called by key_pressed_method in gui'''
        self.is_update_step_value = not self.is_update_step_value 
        self.is_left_algo = True
        data = {'block': block, 'cate': cate, 'is_correct': True, 'resp_cost': resp_cost,  
                'steps_value': steps_value, 'target_road': self.board.current_target_road()
                }
        self.create_trial(**data)
        
    def handle_failure(self):
        '''处理用户判断失败, called by key_pressed_method in gui'''
        self.is_update_step_value = True #需要更新阶梯变量, 以进行下一次刺激显示 
        self.is_left_algo = False         #按右侧方式更新阶梯变量值
        
        data = {'block': block, 'cate': cate, 'is_correct': True, 'resp_cost': resp_cost,  
                'steps_value': steps_value, 'target_road': self.board.current_target_road()
                }
        self.create_trial(**data)
                    
    def is_target_road_real(self):
        return self.board.is_target_road_real()              
            
            
    def build_step_process(self):
        return StepProcess()            
    
    def save_demo(self):
        demo = Demo(param=self.param)
        demo.save()
        return demo   
    
    def create_block(self, **data): #TODO...
        '''进入阶梯循环过程之前调用该方法'''
        block = Block(data)
        return block        
    
    def create_trial(self, **data): #TODO...
        trial = Trial(data)
        if not hasattr(self, 'trial_querylist'):
            self.trial_querylist = []
        self.trial_querylist.append(trial)
        
#     def next_trial(self, ):
#         '''每一次刺激试验为1.6s. 该方法在单独的线程中被循环调用'''
#         # 刷新控制参数, 为下一次1.6s的刺激显示作准备
#         self.board.change_params()         
#         self.gui.draw(self.board)
#         self.wait()
        
    #重置线程flag标志位为False, 以使得signal.wait调用有效.   
    #等待1.6s, 以待用户进行键盘操作判断目标路名真/假并唤醒  
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
    
        