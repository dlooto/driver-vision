#coding=utf-8
#!/usr/bin/env python

#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 22, 2015, by Junn
#

from Tkinter import *           # 导入 Tkinter 库
import maths
from config import *
import subprocess
from vision.demos import StaticSingleDemoThread, DynamicSingleDemoThread
from vision.multi_demos import StaticMultiDemoThread, DynamicMultiDemoThread
from vision.models import TrialParam
from vision.trials import Board


def _create_circle(self, x, y, r, **kwargs): 
    '''通过圆心坐标(x,y)和半径r画圆'''
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

def _create_rectangle(self, x, y, w, h, **kwargs): 
    '''通过矩形中心点坐标(x,y)和矩形宽高(w,h)画矩形'''
    return self.create_rectangle(x-w/2, y-h/2, x+w/2, y+h/2, **kwargs)

Canvas.create_circle = _create_circle
Canvas.create_rectangle_pro = _create_rectangle


class GUI(Tk):
    '''基础Gui控制类'''
    
    def __init__(self):
        Tk.__init__(self)
        self.init_window()
        
    def init_window(self):
        '''初始化窗口: 绘制试验提示信息等'''
        
        self.config(bg=face_background) #设置窗体背景颜色
        self.geometry("%dx%d" % (FACE_SIZE['w'], FACE_SIZE['h']))
        self.cv = Canvas(self, width=FACE_SIZE['w'], height=FACE_SIZE['h'], background=face_background) #灰白色
        self.cv.widget_list = [] # 画布上的组件字典
        
        self.prompt = Label(self, TRIAL_START_PROMPT)
        self.prompt.pack(pady=50)
        
        self.start_button = Label(self, START_BUTTON, relief=RAISED) #使用Button有些Fuck, 改用Label
        self.start_button.pack(pady=250)
        self.start_button.bind('<Button-1>', self.start)
        
        self.bind_keys()
        
      
    def build_demo_thread(self):
        param = TrialParam.objects.latest_coming()
        if not param:
            raise Exception(u'请先设置有效的试验参数')
        param.be_executed()
        
        if param.is_static() and param.is_single():
            return StaticSingleDemoThread(self, param)   #静态单路牌
        if param.is_static() and not param.is_single():
            return StaticMultiDemoThread(self, param)    #静态多路牌
        if not param.is_static() and param.is_single():
            return DynamicSingleDemoThread(self, param)  #动态单路牌
        
        return DynamicMultiDemoThread(self, param)       #动态多路牌             
        
    def erase_all(self):
        for tk_id in self.cv.widget_list:
            self.cv.delete(tk_id)
        self.cv.widget_list = []
        self.cv.update()
        
    def draw_target_seat(self, target_seat, board):
        '''绘制目标路名提示信息'''
        self.erase_all()
        #绘制文字
        txt_pos = PROMPT_POS[0], PROMPT_POS[1]-board.height/2-40  #字体尺寸为40, 所以上移30
        tk_id1 = self.cv.create_text(txt_pos, text='%s%s' % (TARGET_ITEM_PROMPT['text'], target_seat), 
                                    fill=TARGET_ITEM_PROMPT['fill'], font=TARGET_ITEM_PROMPT['font'])
        self.cv.widget_list.append(tk_id1)
        
        #绘制路牌及路名
        self.draw_prompt_boards(board)
        
        self.cv.update()
        
    def draw_target_board(self, multi_board, board_key, tseat):
        '''多路牌时绘制出目标路牌提示
        @param board_key:     目标路牌标识
        @param multi_board:   多路牌对象
        @param tseat: 目标路名位置
        '''
        self.erase_all()
        txt_pos = PROMPT_POS[0], PROMPT_POS[1]-150
        tk_id1 = self.cv.create_text(txt_pos, text='%s%s-%s' % (TARGET_ITEM_PROMPT['text'], board_key, tseat), 
                                    fill=TARGET_ITEM_PROMPT['fill'], font=TARGET_ITEM_PROMPT['font'])
        self.cv.widget_list.append(tk_id1)        
        
        #绘制多路牌
        for iboard in multi_board.prompt_board_dict.values():
            self.draw_prompt_boards(iboard)
        
        self.cv.update()
        
        
    def draw_all(self, board, wpoint):
        self.erase_all()
        self.draw_wpoint(wpoint)
        self.draw_board(board)
        self.cv.update()     
        
    def draw_wpoint(self, wpoint):
        '''绘制注视点'''
        wp_id = self.cv.create_circle(wpoint.pos[0], wpoint.pos[1], wpoint.radius, 
                                      fill=wpoint.fill, outline=wpoint.outline)
        self.cv.widget_list.append(wp_id)
        
    def draw_board(self, board):
        '''将路牌绘制在屏幕上'''  
        if isinstance(board, Board):
            self._draw_single_board(board)
        else:
            self._draw_multi_board(board)    
            
    def _draw_multi_board(self, multi_board):
        for iboard in multi_board.board_dict.values():
            self._draw_single_board(iboard)            
            
    def _draw_single_board(self, board):
        # 绘制路牌面板
        tk_id = self.cv.create_rectangle_pro(
            board.pos[0], board.pos[1], board.width, board.height, fill=board_color, outline=board_color
        )
        self.cv.widget_list.append(tk_id)
        
        # 绘制所有路名
        for road in board.road_dict.values():
            road_font = DEFAULT_ROAD_FONT[0], int(round(road.size, 0))
            road_color = DEFAULT_ROAD_COLOR
            tk_id = self.cv.create_text(road.pos, text=road.name, fill=road_color, font=road_font)
            self.cv.widget_list.append(tk_id)
            
    def draw_prompt_boards(self, board):
        '''将路牌绘制在屏幕上'''  
        tk_id = self.cv.create_rectangle_pro(
            board.pos[0], board.pos[1], board.width, board.height, 
            fill=board_color, outline=board_color
        )
        self.cv.widget_list.append(tk_id)
        
        #绘制所有路名
        for road in board.prompt_road_dict.values():
            road_font = DEFAULT_ROAD_FONT[0], int(round(road.size, 0))
            road_color = TARGET_ROAD_COLOR if road.is_target else DEFAULT_ROAD_COLOR
            tk_id = self.cv.create_text(road.pos, text=road.name, fill=road_color, font=road_font)
            self.cv.widget_list.append(tk_id)
            
           
    def draw_gameover(self):
        gover = TRIAL_END_PROMPT   
        tk_id = self.cv.create_text(gover['pos'], text=gover['text'], 
                                    fill=gover['fill'], font=gover['font'])
        self.cv.widget_list.append(tk_id)
        
    def start(self, e):
        '''点击按钮开始试验. 点击开始前, 需要先设置好试验参数.
        '''
        if hasattr(self, 'demo_thread') and self.demo_thread and self.demo_thread.is_started:
            return
        
        self.demo_thread = self.build_demo_thread()
        
        # 清屏
        self.prompt.destroy()
        self.start_button.destroy()
        self.cv.pack()
        self.erase_all()

        # 启动试验线程
        self.demo_thread.start()
        self.stop()    
        
    def stop(self, e=None):
        self.demo_thread.is_started = False
        self.erase_all()
        self.draw_gameover()
    
    def bind_keys(self):
        self.bind('<Key-Left>',     self._press_left)       #左
        self.bind('<Key-Right>',    self._press_right)      #右
        self.bind('<KeyPress-y>',   self._press_y)          #y键
        self.bind('<KeyPress-n>',   self._press_n)          #n键
        
        self.bind('<KeyPress-S>',   self.start)     #开始键
        self.bind('<KeyPress-Q>',   self.stop)      #结束键
                
        
    def _press_left(self, e):
        print 'Left:', e.keysym 
    def _press_right(self, e):
        print 'Right: ', e.keysym
        
    def _press_y(self, e):
        '''用户按下Y键, 判断目标项为真路名'''
        
        print '%s Pressed' % e.keysym
        is_correct = self.demo_thread.is_judge_correct(is_real=True)
        self._extra_keypressed(is_correct)  
        
    def _press_n(self, e):
        '''用户按下N键, 判断目标项为假路名'''
        
        print '%s Pressed' % e.keysym
        is_correct = self.demo_thread.is_judge_correct(is_real=False)
        self._extra_keypressed(is_correct)
        
    def _extra_keypressed(self, is_correct):
        #self.play_voice(is_correct)
        self.demo_thread.handle_judge(is_correct) #用户判断处理    
                  
        ## 唤醒线程, 中断1.6s的显示进入下一个1.6s
        self.demo_thread.awake()        
                
        
    def play_voice(self, success):
        if success:
            subprocess.call(["afplay", AUD_PATH['T']])
        else:
            subprocess.call(["afplay", AUD_PATH['F']])
        
## 开始新的实验
def run():
    global gui
    gui = GUI()
    gui.title('Vision Trial 视觉测试')
    gui.mainloop()

# 可不通过该main入口执行, 改为命令: python manage.py run_trial
if __name__ == '__main__':
    run()




