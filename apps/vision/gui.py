#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

from Tkinter import *           # 导入 Tkinter 库
import maths
from config import *
import time
import subprocess
from vision.trials import WatchPoint, Board, DemoThread


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
    #eccent = 6                  #离心率              
    #board = None
    
    def __init__(self):
        Tk.__init__(self)
        self.is_started = False              #实验进行状态, 默认为未开始
        self.init_window()
        
        # init elements
        self.watch_point = WatchPoint()
        self.board = Board()
        
    def init_window(self):
        '''初始化窗口: 绘制试验提示信息等'''
        
        self.config(bg=face_background) #设置窗体背景颜色
        self.geometry("%dx%d" % (FACE_SIZE['w'], FACE_SIZE['h']))
        self.cv = Canvas(self, width=FACE_SIZE['w'], height=FACE_SIZE['h'], background=face_background) #灰白色
        self.cv.widget_dict = {} # 画布上的组件字典
        
        self.prompt = Label(self, TRIAL_START_PROMPT)
        self.prompt.pack(pady=50)
        
        self.start_button = Label(self, START_BUTTON, relief=RAISED) #使用Button有些Fuck, 改用Label
        self.start_button.pack(pady=250)
        self.start_button.bind('<Button-1>', self.start)
        
        self.bind_keys()
        
        
    def draw_all(self):
        self.watch_point.draw(self.cv)
        self.board.draw(self.cv)
        
    def draw_gameover(self):
        gover = TRIAL_END_PROMPT   
        tk_id = self.cv.create_text(gover['pos'], text=gover['text'], 
                                    fill=gover['fill'], font=gover['font'])
        self.cv.widget_dict[tk_id] = gover
        
    def erase_all(self):
        for tk_id in self.cv.widget_dict.keys():
            self.cv.delete(tk_id)
        self.cv.widget_dict = {}    
    
    def init_params(self):
        pass
    
    def flash_data(self):
        '''刷新路牌(及上面的路名)和注视点数据内容, 以开始下一个1.6s的刺激显示 '''
        
        self.board.flash_data((BOARD_POS[0], BOARD_POS[1]+50), ('A', 'C', 'D', 'F', 'H'), 'H')
        self.watch_point.flash_data()    
        
    def new_trial(self):
        '''每一次刺激试验为1.6s. 该方法在单独的线程中被循环调用'''
        
        self.flash_data()
        self.erase_all()
        #time.sleep(show_interval)   #just for testing. remove later...
        
        self.draw_all()
        self.cv.update()
        
        time.sleep(show_interval)  #一次刺激显示有1.6s        
    
    def get_eccent(self):
        '''计算离心率: 注视点到目标项的中心点的半径距离，单位为度'''   
         
        road = self.board.get_target_road()
        #or target_board
        return maths.dist(self.watch_point, road.pos)
        # or return self.eccent
        
    def stop(self, e):
        self.is_started = False
        self.erase_all()
        self.draw_gameover()
    
    def start(self, e):
        '''点击按钮开始试验'''
        self.is_started = True
        
        # 清屏
        self.prompt.destroy()
        self.start_button.destroy()
        self.cv.pack()
        self.erase_all()
        
        # 启动试验线程
        DemoThread(self).start()
        
    def bind_keys(self):
        self.bind('<Key-Left>',     self._press_left)     #左
        self.bind('<Key-Right>',    self._press_right)   #右
        self.bind('<KeyPress-y>',   self._press_y)      #y键
        self.bind('<KeyPress-n>',   self._press_n)      #n键
        
        self.bind('<KeyPress-S>',   self.start)     #开始键
        self.bind('<KeyPress-Q>',   self.stop)      #结束键
                
        
    def _press_left(self, e):
        print 'Left:', e.keysym 
        
    def _press_right(self, e):
        print 'Right: ', e.keysym
        
    def _press_y(self, e):
        '''用户识别目标为 真'''
        subprocess.call(["afplay", AUD_PATH['T']])
        print 'y: ', e.keysym
        
    def _press_n(self, e):
        '''用户识别目标为 假'''
        subprocess.call(["afplay", AUD_PATH['F']])
        print 'n: ', e.keysym
        
        
class SingleStaticDemo(GUI):
    '''单路静态实验'''
    pass

class SingleDynamicDemo(GUI):
    pass


def new_demo():
    '''开始新的实验
    '''
    global gui
    gui = GUI()
    gui.title('Vision Trial 视觉测试')
    gui.mainloop()

if __name__ == '__main__':
    new_demo()




