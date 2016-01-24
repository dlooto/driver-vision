#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#

from utils.eggs import float_list_to_str

class StepAlgo(object):
    '''阶梯算法过程基类'''
    
    label = ''
    
    def __init__(self, board, wpoint):
        self.board = board
        self.wpoint = wpoint
        
    def print_prompt(self): #输出提示 
        print('\n%s过程开始...' % self.label)

    def extend_block_data(self, block_data):
        pass
    
    def init_boards(self):
        '''为多路牌时从board_repos重新加载路牌, 以替代在MultiBoard初始构建时无需初始化board_dict''' 
        self.board.reload_boards()
        self.init_others()
            
    def init_others(self):
        pass
    
    def prepare_steping(self):
        '''阶梯过程开始前的准备工作'''
        pass
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        pass
    
    def flash_contents(self):
        self.board.flash_road_names()
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        pass
    
    def set_velocity(self, velocity):
        '''动态阶梯控制过程需要该方法'''
        self.board.set_move_velocity(velocity)    #设置运动速度值
    
            
class SpaceStepAlgo(StepAlgo):
    '''关键间距阶梯算法'''
    
    label = u'求关键间距'
    
    def __init__(self, board, wpoint, space_scale_type):
        StepAlgo.__init__(self, board, wpoint)
        self.space_scale_type = space_scale_type
    
    def extend_block_data(self, block_data):
        extra_data = {
            'cate':  'R', 
            'N':     self.board.count_flanker_items(), 
            'S':     self.board.get_item_size(), 
            'V':     self.board.get_move_velocity(),
        }
        block_data.update(extra_data)
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return float_list_to_str(self.board.get_item_spacings())
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        
        update_all = True
        if self.space_scale_type == 'R2':   #R1: 同时缩放, R2: 逐一缩放
            update_all = False
             
        self.board.update_flanker_spacings(is_left_algo, update_all=update_all)
        print 'Spacing changed:', 'Left' if is_left_algo else 'Right', \
            self.board.get_item_spacings()
            
class NumberStepAlgo(StepAlgo):
    '''数量阈值阶梯算法'''
    
    label = u'求数量阈值'
    
    def extend_block_data(self, block_data):
        '''block数据中添加额外的数据'''
        extra_data = {
            'cate': 'N', 
            'S':    self.board.get_item_size(), 
            'V':    self.board.get_move_velocity(),
            # 'R': 待确定. 目前间距为统一变化
        }
        block_data.update(extra_data)
        
    def prepare_steping(self):
        self.board.clear_queue() #清空辅助队列, 用于干扰项增减(单路牌中为路名, 多路牌中为路牌增减)
        
    def get_steps_value(self):
        '''返回阶梯变化值. 此处为干扰项数量'''
        return self.board.count_flanker_items()
        
    def update_vars(self, is_left_algo):
        self.board.update_flanker_numbers(is_left_algo)
        print 'Flanker items:', 'Left' if is_left_algo else 'Right', self.board.count_flanker_items()
            
        
class SizeStepAlgo(StepAlgo):
    '''尺寸阶梯算法: 求尺寸阈值'''
    
    label = u'求尺寸阈值'
    
    def __init__(self, board, wpoint, space_scale):
        StepAlgo.__init__(self, board, wpoint)
        self.board.space_scale = space_scale #间距是否缩放
    
    def extend_block_data(self, block_data):
        extra_data = {
            'cate': 'S', #求尺寸阈值
            'N':    self.board.count_flanker_items(), 
            'V':    self.board.get_move_velocity(),
            # 'R':  置空, 间距随路名尺寸变化而变化
        }
        block_data.update(extra_data)
    
    def prepare_steping(self):
        '''单路牌时每一轮阶梯过程开始, 将路牌尺寸还原'''
        self.board.restore_size()
    
    def init_others(self): #仅多路牌时使用该方法
        board_size = self.board.board_size
        ori_scale = self.board.board_scale
        ori_road_size = self.board.road_size
        board_list = self.board.board_dict.values()
        for i in range(len(board_list)): #各路牌尺寸还原
            board_list[i].width, board_list[i].height = board_size[0] * ori_scale**i, board_size[1] * ori_scale**i,   
            board_list[i].road_size = ori_road_size * ori_scale**i
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return self.board.get_item_size()
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        self.board.update_items_size(is_left_algo)
        print 'Item size:', 'Left' if is_left_algo else 'Right', self.board.get_item_size()

class VelocityStepAlgo(StepAlgo):
    '''速度阶梯算法: 动态敏感度'''
    
    label = u'求动态敏感度阈值'
    
    def extend_block_data(self, block_data):
        extra_data = {
            'cate': 'V',
            # 'R':  置空, 间距随路名尺寸变化而变化
        }
        block_data.update(extra_data)
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return self.board.get_move_velocity()
    
    def flash_contents(self):
        self.board.flash_road_names()
        self.board.random_move_direction()
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        self.board.change_items_velocity(is_left_algo)
        print 'Velocity:', 'Left' if is_left_algo else 'Right', self.board.get_move_velocity()
  
