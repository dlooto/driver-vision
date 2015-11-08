#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Nov 8, 2015, by Junn
#
from vision.config import STEPS_COUNT

step_count = STEPS_COUNT 

class StepProcess(object):
    '''阶梯算法父类'''
    
    def execute(self):
        pass
#         '''40次阶梯法过程'''
#         for r in STEPS_COUNT:
#             self.change_params(d, self.board.get_eccent(), self.board.get_angle())     
#             self.gui.draw(self.board)
#             self.wait()   

class NstepProcess(StepProcess):
    pass

class SstepProcess(StepProcess):
    pass

class RstepProcess(StepProcess):
    
    def __init__(self, demo, block):
        self.demo = demo
        self.block = block
        
    def execute(self):        
        for r in step_count:
            self.demo.change_params(d, self.board.get_eccent(), self.board.get_angle())     
            self.demo.draw(self.board)
            self.wait()  

class VstepProcess(StepProcess):
    pass
