#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

from Tkinter import *           # 导入 Tkinter 库
import maths
from config import *
import random



def _create_circle(self, x, y, r, **kwargs): 
    '''通过圆心坐标(x,y)和半径r画圆'''
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

def _create_rectangle(self, x, y, w, h, **kwargs): 
    '''通过矩形中心点坐标(x,y)和矩形宽高(w,h)画矩形'''
    return self.create_rectangle(x-w/2, y-h/2, x+w/2, y+h/2, **kwargs)

Canvas.create_circle = _create_circle
Canvas.create_rectangle_pro = _create_rectangle

class GUI(Tk):
    '''一次完整的实验, 基础父类'''
    
    # single or multi, static or dynamic, determined by subclass
    
    watch_pos = None            #注视点坐标           default 
    show_interval = None        #显示时间, 毫秒单位    default
    eccent = 6                  #离心率              
    board = None
    
    def __init__(self):
        Tk.__init__(self)
        
        self.is_started = False              #实验进行状态, 默认为未开始
        self.cv = Canvas(self, width=FACE_SIZE['w'], height=FACE_SIZE['h'], background=face_background) #灰白色
        self.cv.pack()
        
        self.init_watch_point()
        self.init_board()
    
    def __init1__(self, show_interval=1.6, eccent=6, watch_pos=(100,100)):
        self.show_interval = show_interval * 1000
        self.eccent = eccent
        self.watch_pos = watch_pos
        super().__init__()
    
    def init_watch_point(self):
        self.cv.create_circle(WATCH_POS[0], WATCH_POS[1], 5, fill=watch_color, outline=watch_color) #注视点
    
    def init_board(self): #TODO: change this later into Board object...
        #self.cv.create_rectangle_pro(BOARD_POS[0], BOARD_POS[1], BOARD_SIZE['w'], BOARD_SIZE['h'], fill=board_color, outline=board_color)
        self.board = Board()
        self.board.draw(self.cv)
    
    def init_params(self):
        pass
    
    def gen_board(self):
        '''生成路牌. 
        每个1.6s要重新生成一个路牌'''
        self.board = Board()
        
     
    def get_eccent(self):
        '''计算离心率: 注视点到目标项的中心点的半径距离，单位为度'''   
         
        road = self.board.get_target_road()
        #or target_board
        return maths.dist(self.watch_pos, road.pos)
        # or return self.eccent
        
    def new_trial(self):
        '''新生成一次1.6s的实验'''
        return Trial()
        
    def stop(self):
        self.is_started = False
    
    def start(self):
        #self.current_trial = self.new_trial()
        #self.is_started = True
        self.board.draw()
        
        
class Trial(object):
    '''1.6s内的一次刺激实验'''
    
    def __init__(self):
        pass        
              

class SingleStaticDemo(GUI):
    '''单路静态实验'''
    pass

class SingleDynamicDemo(GUI):
    pass

class Board(object):
    '''路牌'''
    
    pos = 100, 100              #中心点坐标, 即路牌位置
    angle = 30                  #路牌初始角度, 在0,30, 60等中取值, 单位度
    width = 280                 #路牌宽度
    height = 200                #路牌高度
    
    road_dict = None            #路名列表
    target_road = None               #目标项
    
    #BOARD_POS[0], BOARD_POS[1], BOARD_SIZE['w'], BOARD_SIZE['h'], fill=board_color, outline=board_color
    def __init__(self, pos=BOARD_POS, width=BOARD_SIZE['w'], height=BOARD_SIZE['h'], angle=0):
        self.pos = pos
        self.width = width
        self.height = height
        self.angle = angle
        
        self.init_road_list(('A', 'D', 'H'), 'A')
        self.set_target_road('A')
    
    def move(self, dx, dy):
        '''路牌移动. dx = p2.x - p1.x, dy = p2.y - p1.y.
        erase()再draw(), 或者canvas.move(board)再canvas.move(roads)
        '''
        pass
    
    def draw(self, canvas):
        '''显示在屏幕上'''  
        canvas.create_rectangle_pro(self.pos[0], self.pos[1], self.width, self.height, fill=board_color, outline=board_color)
        self._draw_roads(canvas)
            
            
    def _draw_roads(self, canvas):
        for road in self.road_dict.values():
            road.draw(canvas)
                
    def erase(self):
        '''擦除路牌, 开始下一个1.6s的显示. 擦除路牌同时擦除所有路名'''
        pass            
    
    def init_road_list(self, marks, target):
        '''从DB随机选择num个路名, marks指定路名所在位置, 如('A', 'B', 'D', 'G')
        target表示目标项, 如target='B'
        '''
        choice_roads = DEFAULT_ROADS
        self.road_dict = {}
        for mark in marks:
            road_name = get_random_road(choice_roads)
            self.road_dict[mark] = Road(road_name, self.pos_xx(mark))
            choice_roads.remove(road_name)
        self.road_dict.get(target).is_target = True   
            
    
    def clear_road_list(self):
        pass
    
    def set_target_road(self, mark): 
        self.road_dict.get(mark).is_target = True  
        
    
    def get_target_road(self):
        return self.target_road
    
    def get_road_num(self):
        return len(self.road_dict)
    
    def pos_a(self):
        return self.pos[0]-80, self.pos[1]+10
    def pos_b(self):
        return self.pos[0]-80, self.pos[1]+35
    def pos_c(self):
        return self.pos[0]-80, self.pos[1]+60
    def pos_d(self):
        return self.pos[0]+80, self.pos[1]+10
    def pos_e(self):
        return self.pos[0]+80, self.pos[1]+35
    def pos_f(self):
        return self.pos[0]+80, self.pos[1]+60
    def pos_g(self):
        return self.pos[0], self.pos[1]-70
    def pos_h(self):
        return self.pos[0], self.pos[1]-45
    
    def pos_xx(self, mark):
        mt = 'pos_%s' % mark.lower()
        return getattr(self, mt)()
    

        
DEFAULT_ROADS = [u'交大路', u'川大路', u'咚咚路', u'成创路', u'Mac路', 
                 u'胜利路', u'飞天路', u'乳香路', u'宁夏路', u'创业路']
def get_random_road(choice_roads):
        return random.choice(choice_roads)


class Road(object):
    name = ''           #路名   
    size = 15           #路名尺寸, 指字体大小, 单位px
    pos = 0, 0          #路名中心点在路牌上的位置坐标
    is_target = False   #是否是目标路名
    
    def __init__(self, name, pos, size=15, is_target=False):
        self.name = name
        self.pos = pos
        self.size = size
        self.is_target = is_target
    
    def draw(self, canvas):
        '''显示在屏幕上'''  #调用画布进行绘制...
        canvas.create_text(self.pos, text=self.name, fill=road_color, font=road_font)
        
    def erase(self):
        '''擦除路名'''
        pass            
    
    def dist_with(self, a_road):
        '''计算路名间距'''
        pass
    
    def __unicode__(self):
        return self.name, self.pos, self.is_target
    
class Move():
    '''运动模式'''
    v = 1               #运动速率

class Tester():
    pass

def press_left(e):
    print 'Left:', e.keysym 
    
def press_right(e):
    print 'Right: ', e.keysym

def new_demo():
    '''开始新的实验
    '''
    global gui
    gui = GUI()
    gui.title('Vision Trial 视觉测试')
    gui.bind('<Key-Left>', press_left)
    gui.bind('<Key-Right>', press_right)
    gui.mainloop()

if __name__ == '__main__':
    new_demo()


      



