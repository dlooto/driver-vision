#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 23, 2015, by Junn
#


from Tkinter import *           # 导入 Tkinter 库
import time
from vision import maths
from config import *
# from PIL import ImageTk


root = Tk()                     # 创建窗口对象的背景色
root.wm_title('Vision Trial 视觉测试')

# 属性: backgroud, font, bitmap, padx, relief, underline
# l1 = Label(root, text='注视点', background='red')
# board = Label(root, text='路牌', background='yellow') # or blue
# 
# def show_label():
#     global root
#     s = Label(root, text='Hello Python')
#     s.pack()
#     
# # b1 = Button(root, text='开始试验', command=show_label)
# b1 = Button(root, text='开始试验')
# # b1.bind()  #可使用该bind方法替代
# 
# b1['background'] = '#0866B9'
# b1['width'] = 20
# b1['height'] = 30
# 
# # 将部件放置到主窗口中
# l1.pack() #找到合适的位置放置组件
# board.pack()
# b1.pack()

# Label(root, text='Username').grid(row=0, sticky=W)
# Entry(root).grid(row=0, column=1, sticky=E)
# Button(root, text='Login').grid(row=2, column=1, sticky=E)  #grid与pack不能同时使用

# t = Text(root, width=50, height=30)
# t.pack()

## Canvas

# f = Toplevel(root, width=30, height=20)
# f.title('TopLevel')
# lf = Label(f, text='我是TopLevel Label')
# lf.pack()

# c = Canvas(root, width=1024, height=800, background='#E4E4E4')
# c.create_line(0, 0, 200, 100)
# c.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

# image = Image.open("../../static/vision/img/board_t_1.jpg") 
# im = ImageTk.PhotoImage(image)  
# image = c.create_image(50, 50, image=image)

def _create_circle(self, x, y, r, **kwargs): 
    '''通过圆心坐标(x,y)和半径r画圆'''
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

def _create_rectangle(self, x, y, w, h, **kwargs): 
    '''通过矩形中心点坐标(x,y)和矩形宽高(w,h)画矩形'''
    return self.create_rectangle(x-w/2, y-h/2, x+w/2, y+h/2, **kwargs)

Canvas.create_circle = _create_circle
Canvas.create_rectangle_pro = _create_rectangle


# board_color = "#0866B9"
road_color = DEFAULT_ROAD_COLOR
# watch_color = 'red' 
# 
# # 试验界面窗口默认尺寸
# FACE_SIZE = {
#     'w': 1024,
#     'h': 768
# }
# face_background = '#F3F9FF'  #主窗口背景颜色
# 
# BOARD_SIZE = {  #小路牌默认尺寸, bs_w, bs_h
#     'w': 280,
#     'h': 200             
# }
# BOARD_SIZE_B = {  #大路牌默认尺寸
#     'w': 420,
#     'h': 300             
# }
# 
# DEFAULT_ROAD_FONT = ("Helvetica", 15)
road_font = DEFAULT_ROAD_FONT
# 
# 
# WATCH_POS = FACE_SIZE['w']/2, FACE_SIZE['h']/2  #默认注视点坐标
# BOARD_POS = WATCH_POS[0]+200, WATCH_POS[1]      #默认路牌中心点坐标,  bp_x, bp_y
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

c = Canvas(root, width=FACE_SIZE['w'], height=FACE_SIZE['h'], background=face_background) #灰白色
c.pack()

# c.create_circle(WATCH_POS[0], WATCH_POS[1], 5, fill=watch_color, outline=watch_color) #注视点
# board_id = c.create_rectangle_pro(BOARD_POS[0], BOARD_POS[1], BOARD_SIZE['w'], BOARD_SIZE['h'], fill=board_color, outline=board_color)
#c.create_rectangle_pro(BOARD_SIZE_B['w']/2, BOARD_SIZE_B['h']/2, BOARD_SIZE_B['w'], BOARD_SIZE_B['h'], fill=board_color, outline=board_color)  #大路牌

# 路牌中心点, 测试阶段作为标注
#c.create_circle(BOARD_POS[0], BOARD_POS[1], 2, fill=road_color, outline=road_color)
#c.create_line(BOARD_POS[0]-140, BOARD_POS[1], BOARD_POS[0]+140, BOARD_POS[1],fill=road_color)

# create_text时, 似乎x,y坐标是文字中心点坐标
road_id_G = c.create_text(ROAD_POS['G'], text='成都路', fill=road_color, font=road_font)
road_id_H = c.create_text(ROAD_POS['H'], text='昆明路', fill=road_color, font=road_font)

road_id_A = c.create_text(ROAD_POS['A'], text='交大路', fill=road_color, font=road_font)
road_id_B = c.create_text(ROAD_POS['B'], text='理工路', fill=road_color, font=road_font)
road_id_C = c.create_text(ROAD_POS['C'], text='川大路', fill=road_color, font=road_font)

road_id_D = c.create_text(ROAD_POS['D'], text='念念路', fill=road_color, font=road_font)
road_id_E = c.create_text(ROAD_POS['E'], text='咚咚路', fill=road_color, font=road_font)
road_id_F = c.create_text(ROAD_POS['F'], text='创业路', fill=road_color, font=road_font)

print maths.dist(ROAD_POS['A'], ROAD_POS['B'])
print maths.dist(ROAD_POS['A'], BOARD_POS)

# time.sleep(5)   #在循环内sleep无法立即生效

#替换文字内容
c.itemconfigure(road_id_A, text='电子路')
c.after(2*1000)
c.update()

#移动文字坐标
#Tkinter.Canvas.move(self, item, dx, dy), dx = p2.x - p1.x, dy = p2.y - p1.y
c.move(road_id_A, 10, -10)
c.after(1*1000)
c.update()
c.move(road_id_B, 20, 0)
c.after(1*1000)
c.update()

#移动路牌
inter = 5
dx, dy = 0, inter
for i in range(1000):
    c.move(board_id, dx, dy)
    c.move(road_id_G, dx, dy)
    c.move(road_id_H, dx, dy)
    c.move(road_id_A, dx, dy)
    c.move(road_id_B, dx, dy)
    c.move(road_id_C, dx, dy)
    c.move(road_id_D, dx, dy)
    c.move(road_id_E, dx, dy)
    c.move(road_id_F, dx, dy)
    c.after(1*200)
    c.update()
    
    if i % 20 == 0:
        if (dx, dy) == (0,inter): #向下
            dx, dy = -inter, 0
            continue
        if (dx, dy) == (-inter,0): #向左
            dx, dy = 0, -inter
            continue    
        if (dx, dy) == (0, -inter): #向上
            dx, dy = inter, 0
            continue
        if (dx, dy) == (inter, 0): #向右
            dx, dy = 0, inter
            continue            
            

root.mainloop()                 # 进入消息循环
print 'hello  '                 # THIS can't be executed