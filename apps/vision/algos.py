#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#

from utils.eggs import float_list_to_str

class StepAlgo(object):
    '''阶梯算法过程基类'''
    
    def __init__(self, board):
        self.board = board
        
    def print_prompt(self):
        pass

    def extend_block_data(self, block_data):
        pass
    
    def init_boards(self):
        '''为多路牌时从board_repos重新加载路牌, 以替代在MultiBoard初始构建时无需初始化board_dict''' 
        self.board.reload_boards()     
        self.init_others()
            
    def init_others(self):
        pass
    
    def prepare_steping(self):
        pass
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        pass
    
    def update_vars(self, is_left_algo):
        '''
        更新阶梯变量.
        '''
        pass
            
class SpaceStepAlgo(StepAlgo):
    '''关键间距阶梯算法'''
    
    def print_prompt(self):
        print('\n求关键间距控制过程开始...')

    def extend_block_data(self, block_data):
        extra_data = {
            'cate':  'R', 
            'N':     self.board.count_flanker_items(), 
            'S':     self.board.get_item_size(), 
        }
        block_data.update(extra_data)
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return float_list_to_str(self.board.get_item_spacings())
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        self.board.update_flanker_spacings(is_left_algo)
        print 'Spacing changed:', 'Left' if is_left_algo else 'Right', \
            self.board.get_item_spacings()
            
class NumberStepAlgo(StepAlgo):
    '''数量阈值阶梯算法'''
    
    def print_prompt(self): #打印提示信息
        print('\n求数量阈值控制过程开始...')
        
    def extend_block_data(self, block_data):
        '''block数据中添加额外的数据'''
        extra_data = {
            'cate': 'N', 
            'S':    self.board.get_item_size(), 
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
    
    def print_prompt(self):
        print('\n求尺寸阈值过程开始...')

    def extend_block_data(self, block_data):
        extra_data = {
            'cate': 'S', #求尺寸阈值
            'N':    self.board.count_flanker_items(), 
            # 'R':  置空, 间距随路名尺寸变化而变化
        }
        block_data.update(extra_data)
    
    def init_others(self):
        for board in self.board.board_dict.values():
            board.width, board.height = self.board.board_size  #各路牌尺寸还原
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return self.board.get_item_size()
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        self.board.update_items_size(is_left_algo)
        print 'Item size:', 'Left' if is_left_algo else 'Right', self.board.get_item_size()

class VelocityStepAlgo(StepAlgo):
    '''速度阶梯算法: 动态敏感度'''
    def print_prompt(self):
        pass

    def extend_block_data(self, block_data):
        pass
    
    def prepare_steping(self):
        pass
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        pass
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量'''
        # TODO...
        pass  
