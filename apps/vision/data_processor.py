#coding=utf-8
#
# Copyright (C) 2015-2016  NianNian TECH Co., Ltd. All rights reserved.
# Created on Jan 24, 2016, by Junn
#
import xlwt
from vision.config import *
from utils import times

# SHEET_HEADER = [u'trial_id', u'block_id', u'初始参数', u'运动模式', u'阶梯类型', u'注视点模式', u'注视点VF',  
#                 u'目标位置(D)', u'目标路名', u'路名数量(N)', u'干扰项数量(N)', u'离心率(E)', u'角度(@)',
#                 u'响应时间', u'是否判断正确', u'阶梯值', u'路牌尺寸', u'路名尺寸', 
#                 u'目干间距(R)', u'目标项速度', u'干扰项速度', u'目标项运动方向', u'干扰项运动方向',]

COLS = {
    u'trial_id':    0, 
    u'block_id':    1, 
    u'初始参数':      2, 
    u'运动模式':      3, 
    u'阶梯类型':      4, 
    u'注视点模式':    5, 
    u'注视点VF':     6,  
    u'目标位置(D)':   7, 
    u'目标路名':       8, 
    u'路名数量(N)':    9, 
    u'干扰项数量(N)':  10, 
    u'离心率(E)':     11, 
    u'角度(@)':      12,
    u'响应时间':      13, 
    u'是否判断正确':   14, 
    u'阶梯值':        15, 
    u'路牌尺寸':      16, 
    u'路名尺寸':      17, 
    u'目干间距(R)':   18, 
    u'目标项速度':    19, 
    u'干扰项速度':    20, 
    u'目标项运动方向': 21, 
    u'干扰项运动方向': 22,           
}

def set_style():
    style = xlwt.XFStyle() 
    font = xlwt.Font() 
    font.name = EXCEL_FONT['name'] 
    font.bold = EXCEL_FONT['bold']
    font.color_index = EXCEL_FONT['color_index']
    font.height = EXCEL_FONT['height']
    style.font = font
    return style
EXCEL_STYLE = set_style()

def gen_filename(demo_id, param_id):
    return 'demo%s_%s_%s.xls' % (demo_id, param_id, times.datetime_to_str(times.now(), '%Y%m%d%H%M')) #'%Y%m%d%H%M%S'

def gen_sheetname(param):
    return param.__unicode__()

def export_excel(demo):
    excel_file = xlwt.Workbook()
    sheet = excel_file.add_sheet(gen_sheetname(demo.param))
    
    for k in COLS.keys():
        sheet.write(0, COLS[k], k, EXCEL_STYLE)
    
    row = 1
    for trial in demo.get_all_trials():
        sheet.write(row, COLS['trial_id'],      trial.id)
        sheet.write(row, COLS['block_id'],      trial.block_id)
        sheet.write(row, COLS[u'初始参数'],       trial.param.__unicode__())
        sheet.write(row, COLS[u'运动模式'],       trial.param.move_type)
        sheet.write(row, COLS[u'阶梯类型'],       trial.param.step_scheme)
        sheet.write(row, COLS[u'注视点模式'],      trial.param.wp_scheme)
        #sheet.write(row, COLS[u'注视点VF'],    trial)
        sheet.write(row, COLS[u'目标位置(D)'],  trial.block.tseat)
        sheet.write(row, COLS[u'目标路名'],     trial.target_road)
        sheet.write(row, COLS[u'路名数量(N)'],  trial.get_N())
        #sheet.write(row, COLS[u'干扰项数量(N)'], trial)
        sheet.write(row, COLS[u'离心率(E)'],    trial.block.ee)
        sheet.write(row, COLS[u'角度(@)'],     trial.block.angle)
        sheet.write(row, COLS[u'响应时间'],     trial.resp_cost)
        sheet.write(row, COLS[u'是否判断正确'],  trial.is_correct)
        sheet.write(row, COLS[u'阶梯值'],       trial.steps_value)
        sheet.write(row, COLS[u'路牌尺寸'],     trial.get_S())
        sheet.write(row, COLS[u'路名尺寸'],     trial.get_S())
        sheet.write(row, COLS[u'目干间距(R)'],  trial.get_R())
        sheet.write(row, COLS[u'目标项速度'],    trial.get_V())
        sheet.write(row, COLS[u'干扰项速度'],    trial.get_V()) 
        #sheet.write(row, COLS[u'目标项运动方向'], trial)
        #sheet.write(row, COLS[u'干扰项运动方向'], trial)
        
        row += 1
            
    
    excel_file.save("%s/%s" % (DATA_ROOT, gen_filename(demo.id, demo.param_id)))
    print("Export excel data done.") 
    

