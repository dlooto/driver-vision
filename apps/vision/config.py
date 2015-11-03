#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 24, 2015, by Junn
#
import settings

'''
视觉测试默认参数设置
'''



face_background = '#F3F9FF'  #主窗口背景颜色
board_color = "#0866B9"      #路牌背景颜色
DEFAULT_ROAD_COLOR = 'white'    #路名颜色
TARGET_ROAD_COLOR = 'green'     #目标路名颜色
watch_color = 'red'             #注视点填充颜色
show_interval = 1.6             #默认刺激显示间隔时间, 单位秒

DEFAULT_ROAD_FONT = ("Helvetica", 15)
TRIAL_END_FONT =    ("Helvetica", 35)      #试验结束文字字体

# 试验界面窗口默认尺寸
FACE_SIZE = {
    'w': 1024,
    'h': 768
}

BOARD_SIZE = {  #小路牌默认尺寸, bs_w, bs_h
    'w': 280,
    'h': 200             
}
BOARD_SIZE_B = {  #大路牌默认尺寸
    'w': 420,
    'h': 300             
}

WATCH_POS = FACE_SIZE['w']/2, FACE_SIZE['h']/2  #注视点坐标默认值
BOARD_POS = WATCH_POS[0]+200, WATCH_POS[1]      #路牌中心点坐标默认值,  bp_x, bp_y

ALLOWED_ROAD_SEATS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')

# 路名默认坐标点
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

#试验提示信息
TRIAL_START_PROMPT = { 
    'text': u'点击"开始"按钮进行测试, "真" 为 "y"  假 为 "n" ', 
    'bg': face_background,
    'fg': 'blue',
    'font': ("Helvetica", 30), 
}

TRIAL_END_PROMPT = {
    'text': u'测试结束', 
    'pos':  WATCH_POS,
    'font': ("Helvetica", 35),
    'fill': '#1F90F2'
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
    'T': '%s/%s' % (aud_root, 'tink.wav'),
    'F': '%s/%s' % (aud_root, 'tock.wav')            
}
