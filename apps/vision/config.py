#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All Rights Reserved.
# Created on Oct 24, 2015, by Junn
#

'''#########################
        视觉测试系统参数设置
   ########################
'''

import os
import sys
import math
import settings

## 为解决以下问题而加载: UnicodeEncodeError: 'ascii' codec can't encode ordinal ...
## 尤其出现在print 'Demo thread started:', self.label()中 in run() of demos.py
reload(sys)
sys.setdefaultencoding('utf-8')


# 试验窗口默认尺寸
FACE_SIZE = {
    'w': 1024,  #宽
    'h': 768    #高
}

FRAME_INTERVAL = 1.6            #默认刺激显示间隔时间, 单位秒
STEPS_COUNT = 20                #阶梯算法循环次数
MOVE_SLEEP_TIME = 0.1           #运动模式时路牌每一次移动时间间隔, 单位秒(s)

WPOINT_DEFAULT_VELOCITY = 30    #注视点默认运动速度值
BOARD_DEFAULT_VELOCITY = 40     #路牌默认运动速度值

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

ALLOWED_ROAD_SEATS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
ALLOWED_BOARD_MARKS = ('B1', 'B2', 'B3')  #路牌位置标记, B1位置为最大尺寸路牌, 多路牌时使用

# 路名尺寸最小值和最大值边界(求尺寸阈值时需要)
SIZE_BORDER = 8, 40         

# 路牌尺寸最小值和最大值边界(求尺寸阈值时)
BOARD_SIZE_BORDER = {       
    'min': (56, 40),        #(width, height)
    'max': (420, 300)                      
}    

#路牌运动速度最小值和最大值边界(求动态敏感度阈值时)
VELO_BORDER = {             
    'min': 10.0,        
    'max': 250.0                      
}   
 
## 注视点默认参数设置
WATCH_POINT_SET = { 
    'pos':      (FACE_SIZE['w']/2, FACE_SIZE['h']/2),   #注视点默认坐标值             
    'radius':   5,          #填充半径
    'fill':     'red',      #填充颜色
    'outline':  'red',      #边框颜色
}
watch_pos = WATCH_POINT_SET['pos']  #为后续简化引用, 赋值别名 
 
face_background     = '#F3F9FF'     #主窗口背景颜色
BOARD_FILL_COLOR    = "#0866B9"         #路牌填充颜色
BOARD_OUTLINE_COLOR = "#CDE5FD"         #路牌边框颜色
DEFAULT_ROAD_COLOR  = 'white'    #路名颜色
TARGET_ROAD_COLOR   = '#ff6600'   #目标路名颜色

DEFAULT_ROAD_FONT = ('Microsoft Yahei', 15)      #("Helvetica", 15)
TRIAL_END_FONT =    ('Microsoft Yahei', 35)      #试验结束文字字体


#小路牌默认尺寸, bs_w, bs_h
BOARD_SIZE = {
    'w': 280, 
    'h': 200            
}

#路牌中心点坐标默认值,  bp_x, bp_y
BOARD_POS = watch_pos[0]+200, watch_pos[1]      

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


USER_GUIDE = \
u'''点击 '开始' 按钮进行测试. 操作说明: \n
    若判断目标路名为 '真' 请按 'y' 键,  判断为 '假' 请按 'n' 键 \n 
    动态敏感度试验时, 请按方向键进行路牌运动方向判断. 
''' 

#试验开始提示信息 
TRIAL_START_PROMPT = { 
    'text': USER_GUIDE,
    'bg':   face_background,
    'fg':   '#1F90F2',
    'font': ("Helvetica", 30), 
}

#试验结束提示信息
TRIAL_END_PROMPT = { 
    'text': u'测试结束', 
    'pos':  watch_pos,
    'font': ("Helvetica", 35),
    'fill': '#1F90F2'
}

#目标项位置提示
TARGET_ITEM_PROMPT = {  
    'text':     u'下一轮目标位置为: ', 
    'pos':      (watch_pos[0], watch_pos[1]-300),    #提示文字默认位置 
    'font':     ("Helvetica", 40),
    'fill':     '#1F90F2',
    'interval': 3               #提示停留时间, 单位秒
}

PROMPT_POS = watch_pos  #目标项提示文字坐标

START_BUTTON = {
    'bg':   '#009900',
    'fg':   'white',
    'font': ("Helvetica", 25),
    'text': u'开始',   
    'width': 8,
}

aud_root = '%s/%s' % (settings.MEDIA_ROOT, settings.AUD_DIR)
AUD_PATH = {
    'T': '%s/%s' % (aud_root, 'success.wav'),  #判断正确提示音
    'F': '%s/%s' % (aud_root, 'failure.wav')   #判断错误提示音             
}

DATA_ROOT = os.path.join(settings.PROJECT_ROOT, 'data')

# Excel文件样式设置
EXCEL_FONT = {
    'name':         'Microsoft Yahei',
    'bold':         True,
    'color_index':  4,
    'height':       220,         
}    


