#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All Rights Reserved.
# Created on Oct 24, 2015, by Junn
#

'''#########################
        视觉测试系统参数设置
   ########################
'''

## 为解决以下问题而加载: UnicodeEncodeError: 'ascii' codec can't encode ordinal ...
## 尤其出现在print 'Demo thread started:', self.label()中 in run() of demos.py
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import math
import settings


show_interval = 1.6             #默认刺激显示间隔时间, 单位秒
STEPS_COUNT = 20                #阶梯算法循环次数
MOVE_SLEEP_TIME = 0.1           #运动模式时路牌每一次移动时间间隔, 单位秒(s)

WPOINT_DEFAULT_VELOCITY = 15    #注视点默认运动速度值
BOARD_DEFAULT_VELOCITY = 50     #路牌默认运动速度值

# 直线运动时, 决定x轴坐标的变化方向
X_DIRECTS = (1, 0, -1)

# 直线运动时, 运动方向的随机值范围, 以角度值表示. 决定y轴坐标的变化方向
PRE_MOVE_DIRECTS = (30, 45, 60, 120, 135, 150)

#直线运动斜率值范围
GRADS = [math.tan(math.radians(a)) for a in PRE_MOVE_DIRECTS]

#求关键间距阶梯算法参数
SPACING_PARAM = {
    'left':  0.8,          #左算法变化因子, 间距缩小
    'right': 2             #右算法变化量, 间距增加
}
#尺寸阈值阶梯算法参数
SIZE_PARAM = {
    'left':  0.8,          
    'right': 1.2                       
}
#动态敏感度阶梯算法参数
VELO_PARAM = {
    'left':  1.4,          
    'right': 0.8                         
}

DEFAULT_ECCENTS = (60, 100, 140, 160)               #默认离心率变化值范围
DEFAULT_ANGLES =  (30, 45, 60, 90, 120, 135, 180)   #默认角度值变化范围

### 边界值
SIZE_BORDER = 8, 40         #路名尺寸最小值和最大值边界(求尺寸阈值时需要)

#路牌尺寸最小值和最大值边界(求尺寸阈值时)
BOARD_SIZE_BORDER = {       
    'min': (56, 40),        #(width, height)
    'max': (420, 300)                      
}    

#路牌运动速度最小值和最大值边界(求动态敏感度阈值时)
VELO_BORDER = {             
    'min': 10.0,        
    'max': 250.0                      
}   
 
face_background = '#F3F9FF'     #主窗口背景颜色
board_color = "#0866B9"         #路牌背景颜色
DEFAULT_ROAD_COLOR = 'white'    #路名颜色
TARGET_ROAD_COLOR = '#ff6600'   #目标路名颜色
watch_color = 'red'             #注视点填充颜色

DEFAULT_ROAD_FONT = ('Microsoft Yahei', 15)      #("Helvetica", 15)
TRIAL_END_FONT =    ('Microsoft Yahei', 35)      #试验结束文字字体

# 试验界面窗口默认尺寸
FACE_SIZE = {
    'w': 1024,
    'h': 768
}

#小路牌默认尺寸, bs_w, bs_h
BOARD_SIZE = {
    'w': 280, 
    'h': 200            
}
#大路牌默认尺寸
BOARD_SIZE_B = {  
    'w': 420,
    'h': 300             
}

WATCH_POS = FACE_SIZE['w']/2, FACE_SIZE['h']/2  #注视点坐标默认值
BOARD_POS = WATCH_POS[0]+200, WATCH_POS[1]      #路牌中心点坐标默认值,  bp_x, bp_y

ALLOWED_ROAD_SEATS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
ALLOWED_BOARD_MARKS = ('B1', 'B2', 'B3')  #路牌位置标记, B1位置为最大尺寸路牌, 多路牌时使用

#140*100路牌尺寸. 基础路名位置坐标参考系
ROAD_SEAT_REFER = { 
    'left_x':   30,     #路牌中心点左侧路名与中心点横向距离
    'right_x':  30,     #路牌中心点右侧路名与中心点横向距离
    'a_y':      5,      #A位置路名中心点离路牌中心点的纵向距离
    'blank_y':  5,      #纵向相邻路名间的空白间距, 以路名上下边缘计算
    'g_y':      35      #G位置路名中心点离路牌中心点的纵向距离
}

def scale_refer(factor):
    '''根据不同尺寸缩放因子, 返回不同路名位置坐标参考系'''
    return {
        'left_x':   ROAD_SEAT_REFER['left_x']   * factor,     #路牌中心点左侧路名与中心点横向距离
        'right_x':  ROAD_SEAT_REFER['right_x']  * factor,     #路牌中心点右侧路名与中心点横向距离
        'a_y':      ROAD_SEAT_REFER['a_y']      * factor,     #A位置路名中心点离路牌中心点的纵向距离
        'blank_y':  ROAD_SEAT_REFER['blank_y']  * factor,     #纵向相邻路名间的空白间距, 以路名上下边缘计算  
        'g_y':      ROAD_SEAT_REFER['g_y']      * factor      #G位置路名中心点离路牌中心点的纵向距离
    }

# ## 路名默认坐标参考系设置. 以下已弃用....
# ROAD_SEAT = { #280*200路牌尺寸
#     'left_x':   80,     #路牌中心点左侧路名与中心点横向距离
#     'right_x':  80,     #路牌中心点右侧路名与中心点横向距离
#     'a_y':      10,     #A位置路名中心点离路牌中心点的纵向距离
#     'blank_y':  10,     #纵向相邻路名间的空白间距, 以路名上下边缘计算  
#     'g_y':      70      #G位置路名中心点离路牌中心点的纵向距离
# }
# 
# ROAD_SEAT_B = { #420*300路牌尺寸
#     'left_x':   120,     #路牌中心点左侧路名与中心点横向距离
#     'right_x':  120,     #路牌中心点右侧路名与中心点横向距离
#     'a_y':      15,      #A位置路名中心点离路牌中心点的纵向距离
#     'blank_y':  15,      #纵向相邻路名间的空白间距, 以路名上下边缘计算  
#     'g_y':      105      #G位置路名中心点离路牌中心点的纵向距离
# }

USER_GUIDE = \
u'''点击 '开始' 按钮进行测试. 操作说明: \n
    若判断目标路名为 '真' 请按 'y' 键,  判断为 '假' 请按 'n' 键 \n 
    动态敏感度试验时, 请按方向键进行路牌运动方向判断. 
''' 

TRIAL_START_PROMPT = { #试验开始提示信息 
    'text': USER_GUIDE,
    'bg':   face_background,
    'fg':   '#1F90F2',
    'font': ("Helvetica", 30), 
}

TRIAL_END_PROMPT = { #试验结束提示信息
    'text': u'测试结束', 
    'pos':  WATCH_POS,
    'font': ("Helvetica", 35),
    'fill': '#1F90F2'
}

TARGET_ITEM_PROMPT = {  #目标项位置提示
    'text': u'下一轮目标位置为: ', 
    'pos':  (WATCH_POS[0], WATCH_POS[1]-300),    #提示文字默认位置
    'font': ("Helvetica", 40),
    'fill': '#1F90F2',
    'interval': 3           #提示停留时间, 单位秒
}

PROMPT_POS = WATCH_POS  #目标项提示文字坐标

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


