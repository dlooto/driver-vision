#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#


'''
数学计算公式
'''

def dist(p1, p2):
    '''计算两个坐标点距离'''
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
