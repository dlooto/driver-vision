#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 24, 2015, by Junn
#

'''
GUI工具模块.

'''

from Tkinter import *
from config import *

def _create_circle(self, x, y, r, **kwargs): 
    '''通过圆心坐标(x,y)和半径r画圆'''
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

def _create_rectangle(self, x, y, w, h, **kwargs): 
    '''通过矩形中心点坐标(x,y)和矩形宽高(w,h)画矩形'''
    return self.create_rectangle(x-w/2, y-h/2, x+w/2, y+h/2, **kwargs)

Canvas.create_circle = _create_circle
Canvas.create_rectangle_pro = _create_rectangle

window = Tk()                     # 创建窗口对象的背景色
window.wm_title('Vision Trial 视觉测试')

cv = Canvas(window, width=FACE_SIZE['w'], height=FACE_SIZE['h'], background=face_background) #灰白色
cv.pack()

def mainloop():
    return window.mainloop()