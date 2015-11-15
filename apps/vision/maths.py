#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#
import math


'''
数学计算公式
'''

def dist(p1, p2):
    '''计算两个坐标点距离, p1与p2为两点坐标值,如(x, y)'''
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def angle(p1, p2):  #TODO: 确认该公式的角度方向(正负)是否正确
    '''计算两个坐标点连线与水平线的夹角, p1与p2为两点坐标值,如(x, y)
    返回角度值
    '''
    return math.atan( (p1[1]-p2[1]) / ((p1[0]-p2[0])*1.0)) *180/math.pi



