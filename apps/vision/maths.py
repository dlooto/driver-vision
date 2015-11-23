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
    return round(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5, 2)

def angle(p1, p2):
    '''计算两个坐标点连线与水平线的夹角, p1与p2为两点坐标值,如(x, y)
    返回角度值
    '''
    #return math.atan( (p1[1]-p2[1]) / ((p1[0]-p2[0])*1.0)) *180/math.pi
    dx = p1[0]-p2[0]
    dy = p1[1]-p2[1]
    if dy == 0:
        return 0
    
    if dx == 0: #防止除0情况
        if dy < 0: #p1在p2上方, 
            return 90
        if dy > 0: #p1在p2下方
            return 270
            
    if dx > 0: #二三象限
        return (math.pi + math.atan(dy/dx*1.0) ) * 180/math.pi
    
    #一四象限 dx < 0 
    if dy < 0:
        return math.atan(dy/dx*1.0) * 180/math.pi
    if dy > 0:
        return (2*math.pi + math.atan(dy/dx*1.0)) * 180/math.pi
    

