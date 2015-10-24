#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 24, 2015, by Junn
#

'''
默认参数设置
'''

board_color = "#0866B9"
road_color = 'white'
watch_color = 'red' 

# 试验界面窗口默认尺寸
FACE_SIZE = {
    'w': 1024,
    'h': 768
}
face_background = '#F3F9FF'  #主窗口背景颜色

BOARD_SIZE = {  #小路牌默认尺寸, bs_w, bs_h
    'w': 280,
    'h': 200             
}
BOARD_SIZE_B = {  #大路牌默认尺寸
    'w': 420,
    'h': 300             
}

DEFAULT_ROAD_FONT = ("Helvetica", 15)
road_font = DEFAULT_ROAD_FONT
TRIAL_END_FONT = ("Helvetica", 35)


WATCH_POS = FACE_SIZE['w']/2, FACE_SIZE['h']/2  #默认注视点坐标
BOARD_POS = WATCH_POS[0]+200, WATCH_POS[1]      #默认路牌中心点坐标,  bp_x, bp_y
ROAD_POS = {
    'A': (BOARD_POS[0]-80, BOARD_POS[1]+10),    #路名高度15, 路名相隔间距10 
    'B': (BOARD_POS[0]-80, BOARD_POS[1]+35),
    'C': (BOARD_POS[0]-80, BOARD_POS[1]+60),
    
    'D': (BOARD_POS[0]+80, BOARD_POS[1]+10),
    'E': (BOARD_POS[0]+80, BOARD_POS[1]+35),
    'F': (BOARD_POS[0]+80, BOARD_POS[1]+60),
    
    'G': (BOARD_POS[0],    BOARD_POS[1]-70),
    'H': (BOARD_POS[0],    BOARD_POS[1]-45)
}

