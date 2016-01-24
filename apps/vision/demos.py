#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#

import time
from vision.models import Demo, Block, Trial
from utils import times
from config import *
import threading
from vision.trials import Board, WatchPoint
from vision.algos import SpaceStepAlgo, NumberStepAlgo, SizeStepAlgo,\
    VelocityStepAlgo
from vision.motion import MotionWorker, CircleMoveScheme, SmoothMoveScheme,\
    MixedMoveScheme, DefaultMoveScheme


'''
单路牌试验线程类
'''

class DemoThread(threading.Thread):
    '''父类试验线程对象. 为初始参数,路牌,注视点等的容器
    '''
    is_started = False              #实验进行状态, 默认为未开始
    signal = threading.Event()
    
    param = None      #数据库读取的参数对象
    wpoint = None     #注视点
    board = None      #多路牌时为MultiBoard对象结构, 单路牌时为Board对象结构
    
    #辅助结构
    demo = None
    trial_querylist = []            #缓存trial model对象, 用于批量插入数据
    
    is_left_algo = True             #是否采用左侧算法
    is_update_step_value = True     #是否更新阶梯变量值, 默认更新阶梯变量(!!!重要)
       
    total_trials = 0                #总刺激显示次数
    total_correct_judge = 0         #总正确判断次数
    
    def __init__(self, gui, param):
        threading.Thread.__init__(self)
        
        self.gui = gui
        self.param = param
        
        self.wpoint = self.build_wpoint()
        self.board = self.build_board()
        
        self.board.set_move_scheme(self.build_move_scheme(self.param))
        self.wpoint.set_move_scheme(self.build_wp_move_scheme(self.param))
        
        self.step_algo = self.build_step_algo(self.param.step_scheme)
        
        
    def run(self):
        print 'Demo thread started:', self.param
        
        self.is_started = True              #实验进行状态, 默认为未开始
        self.new_demo_model()               #先构造demo数据对象, 以备阶梯过程中使用
        
        self.step_process(self.param, self.step_algo)
        
        #批量保存block数据, is_started=True 则试验未被中断, 否则被中断
        self.end_demo(is_break=not self.is_started)
        
        print('Demo thread ended')
        
    def build_wpoint(self):
        return WatchPoint()  
        
    def build_board(self):
        '''多路牌情况时需要重写'''
        width, height = self.param.get_board_size()
        return Board(0, 0, self.param.road_size, width=width, height=height,)
    
    def build_step_algo(self, step_scheme):
        if step_scheme not in ('R', 'S', 'N', 'V'):
            raise Exception('Unknown step scheme: %s' % step_scheme)
         
        if step_scheme == 'R': #关键间距      
            return SpaceStepAlgo(self.board, self.wpoint, self.param.space_scale_type)
        if step_scheme == 'N': #数量阈值   
            return NumberStepAlgo(self.board, self.wpoint)
        if step_scheme == 'S': #尺寸阈值
            if self.param.space_type == 'S2': #尺寸阈值2
                return SizeStepAlgo(self.board, self.wpoint, space_scale=True)
            return SizeStepAlgo(self.board, self.wpoint, space_scale=False) #尺寸阈值1
        else:
            return self.build_velocity_step_algo(self.board, self.wpoint)    #动态敏感度     
    
    def build_velocity_step_algo(self, board, wpoint):
        '''为多态重写, 增加该方法'''
        return VelocityStepAlgo(board, wpoint)
    
    def prompt_target_seat(self, tseat):
        '''绘制目标位置提示, 停留3秒'''
        self.board.reset_pos_xy(WATCH_POINT_SET['pos'])
        
        for road in self.board.prompt_road_dict.values():
            road.is_target = False
        self.board.prompt_road_dict[tseat].is_target = True  #便于目标路名红色标注
        
        self.gui.draw_target_seat(tseat, self.board)
        time.sleep(TARGET_ITEM_PROMPT['interval'])
        
    def prompt_target_multi(self, tboard_key, tseat): 
        '''提示目标项位置: 所在路牌及路名
        @param tboard_key: 目标路牌标识, B1/B2/B3
        '''
        print tboard_key, tseat
        
        # set target road
        for iboard in self.board.prompt_board_dict.values():
            for road in iboard.prompt_road_dict.values():
                road.is_target = False
        self.board.prompt_board_dict[tboard_key].prompt_road_dict[tseat].is_target = True
        
        self.gui.draw_target_board(self.board, tboard_key, tseat)  #self.board相当于多个路牌的容器
        time.sleep(TARGET_ITEM_PROMPT['interval'])
 
    def build_move_scheme(self, param):
        '''仅动态模式时需要构建MoveScheme对象'''
        
        if param.is_static():
            return DefaultMoveScheme()
        
        if param.move_type not in ('C', 'S', 'M'):
            raise Exception('Unknown move_type: %s' % param.move_type)
        
        # 求动态敏感度阈值时不进行圆周运动
        if param.move_type == 'C' and param.is_dynamic_sensitivity():
            raise Exception('参数错误: 动态敏感度阶梯过程仅在平滑运动时有效')
            
        if param.move_type == 'C':    #圆周
            return CircleMoveScheme(self.wpoint.pos)
        elif param.move_type == 'S':  #平滑
            return SmoothMoveScheme()
        else: #param.move_type == 'M':
            return MixedMoveScheme()  #混合
        
    def build_wp_move_scheme(self, param):
        '''构建注视点运动模式对象. 注视点目前仅支持平滑运动'''
                
        if param.wp_scheme not in ('L', 'S'):
            raise Exception('Unknown wp_scheme: %s' % param.wp_scheme)
        
        if param.is_static() or param.wp_scheme == 'S':
            return DefaultMoveScheme(v=WPOINT_DEFAULT_VELOCITY)        
        
        if param.wp_scheme == 'L': #直线运动
            return SmoothMoveScheme(v=WPOINT_DEFAULT_VELOCITY)
 
    def start_motion_worker(self):
        '''静态试验中, 需重写该方法为空'''
        self.motion = MotionWorker(self.gui, self.board, self.wpoint)  #后续可考虑从线程池中取出一个...
        self.motion.start()

    def stop_motion_worker(self):
        self.motion.stop()

    def step_process(self, param, step_algo):
        '''阶梯过程. 不同阶梯过程差异使用多态解决. 
        注: 不含动态敏感度阈值计算过程
        '''
        
        # init params
        road_seats, target_seats = param.get_road_seats()
        eccent_list = param.get_eccents()
        angle_list = param.get_angles()
        
        step_algo.print_prompt()
        for tseat in target_seats:
            if not self.is_started: break
            
            self.prompt_target_seat(tseat)
            for velocity in param.get_velocitys():
                step_algo.set_velocity(velocity)    #extend_block_data时需要该参数
                
                for eccent in eccent_list:
                    for angle in angle_list:            
                        self.board.reset_pos(eccent, angle)
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
                        self.deglue()   #阶梯过程前去除粘附
                        
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
                            
                            #刺激显示一帧并进入按键等待. 若为动态模式则开始运动线程.
                            self.show_frame()

                            # 自然等待1.6s(非用户按钮唤醒), 视为用户判断错误
                            if not self.is_awakened():
                                self.current_trial.is_correct = False
                                self.handle_judge(is_correct=False)
                            
                            # 线程唤醒(用户判断或自然等待)后刷新路名, 准备下一帧显示   
                            step_algo.flash_contents()
                            if not self.is_update_step_value:   #不更新阶梯变量, 则直接进行第2次刺激显示
                                continue
                            
                            # 更新阶梯变量
                            step_algo.update_vars(self.is_left_algo)

    def deglue(self):
        self.wpoint.deglue()
        self.board.deglue()                            

    def show_frame(self):
        '''刺激显示一帧. 
        路牌显示后将等待并阻塞后续逻辑执行, 直到用户按键判断或等待1.6s
        '''
        self.gui.draw_all(self.board, self.wpoint)
        
        # 静态时不运作, 动态模式时'开始运动线程'
        self.start_motion_worker()
         
        #等待用户按键判断         
        self.wait()        
        
        #用户按键判断后或自然等待1.6s后, 路牌停止运动
        self.stop_motion_worker()        

    def end_demo(self, is_break=False):
        '''is_break: True-试验被中断, False-试验未被中断. 
        '''
        Trial.objects.bulk_create(self.trial_querylist)
        
        self.demo.time_cost = round(times.time_cost(self.demo.created_time), 1)
        rate = self.total_correct_judge*1.0/self.total_trials if self.total_trials else 0
        self.demo.correct_rate = round(rate, 2)
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
    
    def is_direction_judge_correct(self, direction):
        '''确定用户按键判断是否正确. 若用户的判断值与路牌运动方向一致, 则返回True, 否则返回False
        @param direction: 为用户输入的判断值, 1-用户判断为上, 2-用户判断为下, 3-判断为左, 4-判断为右
        '''
        if self.board.is_same_direction_with(direction):     
            self.current_trial.is_correct = True
            self.total_correct_judge += 1
        else: #判断错误
            self.current_trial.is_correct = False
            
        self.current_trial.resp_cost = times.time_cost(self.current_trial.created_time)
        return self.current_trial.is_correct                      
            
    def new_demo_model(self):
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
        self.signal.wait(FRAME_INTERVAL)
        
    def is_awakened(self):
        '''线程是否被用户按键唤醒, 若刺激显示是自然等待1.6s开始下一帧则未被唤醒, 此时返回False. 
        用户按键做判断后, 线程将被唤醒, 唤醒标识位设置为True, 
        '''
        return self.signal.is_set()      
        
    def awake(self):
        '''唤醒线程. Set the internal flag to true. 
        在用户按键后被调用, 后续将开始下一帧的刺激显示
        '''
        self.signal.set()
        
        
class StaticSingleDemoThread(DemoThread):
    '''静态单路牌'''
    
    #### 静态模式重写以下方法为空   
    def start_motion_worker(self): 
        pass
    
    def stop_motion_worker(self):
        pass
    
    def build_velocity_step_algo(self, board, wpoint): #多态重写
        raise Exception(u'静态模式无动态敏感度阈值阶梯过程')

class DynamicSingleDemoThread(DemoThread):
    '''动态单路牌'''
    
    pass
    
    # 动态敏感度
    

    
        