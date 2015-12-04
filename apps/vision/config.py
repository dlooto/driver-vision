#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 24, 2015, by Junn
#
import settings

'''
视觉测试默认参数设置
'''



face_background = '#F3F9FF'     #主窗口背景颜色
board_color = "#0866B9"         #路牌背景颜色
DEFAULT_ROAD_COLOR = 'white'    #路名颜色
TARGET_ROAD_COLOR = 'white'     #目标路名颜色
watch_color = 'red'             #注视点填充颜色
show_interval = 1.6             #默认刺激显示间隔时间, 单位秒

SPACING_RIGHT_DELTA = 1         #间距变化右算法变化量

STEPS_COUNT = 5                     #阶梯法默认循环次数
DEFAULT_ECCENTS = (6, 10, 14, 16)    #默认离心率变化值范围
DEFAULT_ANGLES =  (30, 45, 60, 90, 120, 135, 180)   #默认角度值变化范围

SIZE_BORDER = 8, 40

DEFAULT_ROAD_FONT = ("Helvetica", 15)
TRIAL_END_FONT =    ("Helvetica", 35)      #试验结束文字字体

# 试验界面窗口默认尺寸
FACE_SIZE = {
    'w': 1024,
    'h': 768
}

#小路牌默认尺寸, bs_w, bs_h
BOARD_SIZE = {  
    'w': 280, #280
    'h': 200  #200           
}
#大路牌默认尺寸
BOARD_SIZE_B = {  
    'w': 420,
    'h': 300             
}

WATCH_POS = FACE_SIZE['w']/2, FACE_SIZE['h']/2  #注视点坐标默认值
BOARD_POS = WATCH_POS[0]+200, WATCH_POS[1]      #路牌中心点坐标默认值,  bp_x, bp_y

ALLOWED_ROAD_SEATS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')

# 路名默认坐标设置
ROAD_SEAT = {
    'left_x':   80,     #路牌中心点左侧路名与中心点横向距离
    'right_x':  80,     #路牌中心点右侧路名与中心点横向距离
    'a_y':      10,     #A位置路名中心点离路牌中心点的纵向距离
    'blank_y':  10,     #纵向相邻路名间的空白间距, 以路名上下边缘计算  
    'g_y':      70      #G位置路名中心点离路牌中心点的纵向距离
}

TRIAL_START_PROMPT = { #试验开始提示信息 
    'text': u'点击"开始"按钮进行测试, "真" 为 "y"  假 为 "n" ', 
    'bg': face_background,
    'fg': '#1F90F2',
    'font': ("Helvetica", 30), 
}

TRIAL_END_PROMPT = { #试验结束提示信息
    'text': u'测试结束', 
    'pos':  WATCH_POS,
    'font': ("Helvetica", 35),
    'fill': '#1F90F2'
}

TARGET_SEAT_PROMPT = {  #目标项位置提示
    'text': u'下一轮目标为: ', 
    'pos':  (WATCH_POS[0], WATCH_POS[1]-300),
    'font': ("Helvetica", 40),
    'fill': '#1F90F2',
    'interval': 3    #提示时间, 单位秒
}

START_BUTTON = {
    'bg':   '#009900',
    'fg':   'white',
    'font': ("Helvetica", 25),
    'text': u'开始',   
    'width': 8,
}

aud_root = '%s/%s' % (settings.MEDIA_ROOT, settings.AUD_DIR)
AUD_PATH = {
    'T': '%s/%s' % (aud_root, 'tink.wav'),  #判断正确提示音
    'F': '%s/%s' % (aud_root, 'tock.wav')   #判断错误提示音             
}


