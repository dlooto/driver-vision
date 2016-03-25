#coding=utf-8
"""
Created on Sep 17, 2014

@author: junn
"""
from django.test import TestCase
from vision import maths

from vision.models import Demo


class PostsUnreadTest(TestCase):

    def setUp(self):
        pass

    def test_gui(self):
        pass

    def test_get_all_posts_unread_count(self):
        print 'unread_dict: \n'

import xlwt
#import xlrd
from utils import times
from vision.config import *

SHEET_NAME = "my_sheet1"
file_name = 'test_%s.xls' % times.datetime_to_str(times.now(), '%Y%m%d%H%M%S')

def test_excel():
    excel_file = xlwt.Workbook()
    sheet = excel_file.add_sheet(SHEET_NAME)
    
    row0 = [u'初始参数', u'目标路名', u'运动模式', u'响应时间', u'判断正确']
    for i in range(0,len(row0)):
        sheet.write(0, i, row0[i], set_style('Microsoft Yahei',220,True))
        
    for row in range(1, 10):
        for col in range(0,10):
            #sheet.write(row, col, random.randrange(0,10))
            sheet.write(row, col, u'中国人路牌位置')
            
    excel_file.save("%s/%s" % (DATA_ROOT, file_name))
    print "Done" 
    
def set_style(name, height, bold=False):
    style = xlwt.XFStyle() # 初始化样式
    
    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    
    style.font = font
    return style    
    
    
def test_export_excel():
    demo = Demo.objects.get(id=788)
    # data_processor.ExcelExporter().export_excel(demo)

    print 'Just test the pycharm....'
    print('ok, let go')  # just for testing Pycharm move line down ...



if __name__ == "__main__":
    pass


