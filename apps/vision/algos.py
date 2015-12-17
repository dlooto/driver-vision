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
    
    #def get_dynamic_road_seats(self, road_seats):
    #    return road_seats

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
            'N':     len(self.board.get_road_seats())-1, 'S': self.board.get_road_size(), 'V': 0.0
        }
        block_data.update(extra_data)
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return float_list_to_str(self.board.get_road_spacings())
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量. 默认返回值为road_seats'''
        self.board.update_flanker_spacings(is_left_algo)
        print 'Spacing changed: ', '0.5r' if is_left_algo else 'r+1', self.board.get_road_spacings()
            
class NumberStepAlgo(StepAlgo):
    '''数量阶梯算法: 求数量阈值'''
    
    def print_prompt(self): #打印提示信息
        print('\n求数量阈值控制过程开始...')
        
    def extend_block_data(self, block_data):
        extra_data = {
            'cate': 'N', 
            'S': self.board.get_road_size(), 'V': 0.0   # 'R': 应该为空, 因间距个数不确定
        }
        block_data.update(extra_data)
        
    def prepare_steping(self):
        self.board.clear_queue() #清空辅助队列, 用于干扰路名增减
        
    def get_steps_value(self):
        '''返回阶梯变化值. 此处为干扰项数量'''
        return len(self.board.get_flanker_roads())
        
    def update_vars(self, is_left_algo):
        self.board.update_flanker_numbers(is_left_algo, self.board.get_road_size())
        print 'Flankers:', 'N+2' if is_left_algo else 'N-1', len(self.board.get_flanker_roads())    
            
        
class SizeStepAlgo(StepAlgo):
    '''尺寸阶梯算法: 求尺寸阈值'''
    
    def print_prompt(self):
        print('\n求尺寸阈值过程开始...')

    def extend_block_data(self, block_data):
        extra_data = {
            'cate': 'S', #求尺寸阈值
            'N':    len(self.board.get_road_seats())-1, 'V': 0.0   # 'R': 置空, 间距随路名尺寸变化而变化
        }
        block_data.update(extra_data)
    
    def get_steps_value(self):
        '''返回阶梯变化值'''
        return self.board.get_road_size()
    
    def update_vars(self, is_left_algo):
        '''更新阶梯变量. 默认返回值为road_seats'''
        # ##
        self.board.update_road_size(is_left_algo)
        print 'Road size:', '*0.8' if is_left_algo else '*1.2', self.board.get_road_size()

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
        '''更新阶梯变量. 默认返回值为road_seats'''
        # TODO...
        pass  
