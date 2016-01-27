#coding=utf-8
#
# Copyright (C) 2015-2016  NianNian TECH Co., Ltd. All rights reserved.
# Created on Jan 24, 2016, by Junn
#

import xlwt
from vision.config import *
from utils import times


# 列名设置
COL = {
    'trial_id':     u'Trial_ID',  
    'block_id':     u'Block_ID', 
    'init_param':   u'初始参数',
    'move_scheme':  u'运动模式',
    'step_scheme':  u'阶梯类型',
    'wp_scheme':    u'注视点模式', 
    'wp_velocity':  u'注视点速度',
    
    'target_seat':  u'目标位置(D)',
    'eccent':       u'离心率(E)',
    'angle':        u'角度', 
    'resp_cost':    u'响应时间',
    'is_correct':   u'是否判断正确', 
    'target_road':  u'目标路名',
    
    # 以下为不同阶梯过程选择不同的列
    'R':   u'目干间距(R)',
    'N':   u'干扰项数量(N)',
    'S':   u'路牌/路名尺寸(S)',
    'V':   u'目标项/干扰项速度(V)',
    'M' :  u'目标项/干扰项运动方向',   
}            

# Excel表格各阈值通用列设置, 数值代表列所在位置
COL_INDEX = {
    'trial_id':    0, 
    'block_id':    1, 
    'init_param':  2, 
    'move_scheme': 3, 
    'step_scheme': 4, 
    'wp_scheme':   5, 
    'wp_velocity': 6,  
    
    'target_seat': 7,  
    'eccent':      8,
    'angle':       9, 
    'resp_cost':   10, 
    'is_correct':  11, 
    'target_road': 12, 
    
    'R': 13,
    'N': 14,
    'S': 15,
    'V': 16,
    'M': 17,
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


def gen_filename(demo_id):
    return 'demo%s_%s.xls' % (demo_id, times.datetime_to_str(times.now(), '%Y%m%d%H%M')) #'%Y%m%d%H%M%S'

def gen_sheetname(param):
    return param.__unicode__()

def build_excel_exporter(step_scheme):
    if step_scheme == 'R':
        return SpaceExcelExporter()
    if step_scheme == 'N':
        return NumberExcelExporter()
    if step_scheme == 'S':
        return SizeExcelExporter()
    if step_scheme == 'V':            
        return VelocityExcelExporter()
    
    raise Exception('Unknown step scheme: %s' % step_scheme)


class ExcelExporter():
    """Excel文件导出管理类"""
    
    def __init__(self):
        self.excel_file = xlwt.Workbook()

    def export_excel(self, demo):
        """ 导出Excel文件 """
        sheet = self.excel_file.add_sheet(gen_sheetname(demo.param))
        
        for k, v in COL_INDEX.items():
            sheet.write(0, v, COL[k], EXCEL_STYLE)
        
        row = 1
        for trial in demo.get_all_trials():
            self._write_common_fields(sheet, trial, row)
            self._write_step_fields(sheet, trial, row)
            row += 1
        
        self.excel_file.save("%s/%s" % (DATA_ROOT, gen_filename(demo.id)))
        print("Data exported success.")

    def _write_common_fields(self, sheet, trial, row):
        """ 写入通用字段 """
        sheet.write(row, COL_INDEX['trial_id'],    trial.id)        # 在指定行列写入数据
        sheet.write(row, COL_INDEX['block_id'],    trial.block_id)
        sheet.write(row, COL_INDEX['init_param'],  trial.param.id)
        sheet.write(row, COL_INDEX['move_scheme'], trial.param.move_type)
        sheet.write(row, COL_INDEX['step_scheme'], trial.param.step_scheme)
        sheet.write(row, COL_INDEX['wp_scheme'],   trial.param.wp_scheme)
        sheet.write(row, COL_INDEX['wp_velocity'], trial.wp_velocity)

        sheet.write(row, COL_INDEX['target_seat'], trial.block.tseat)
        sheet.write(row, COL_INDEX['eccent'],      trial.block.ee)
        sheet.write(row, COL_INDEX['angle'],       trial.block.angle)
        sheet.write(row, COL_INDEX['resp_cost'],   trial.resp_cost)
        sheet.write(row, COL_INDEX['is_correct'],  trial.is_correct)
        sheet.write(row, COL_INDEX['target_road'], trial.target_road)

        sheet.write(row, COL_INDEX['M'],           trial.move_direct)

    def _write_step_fields(self, sheet, trial, row):
        '''写入具体阶梯过程字段'''
        pass


class SpaceExcelExporter(ExcelExporter):
    '''关键间距数据导出'''
    
    def _write_step_fields(self, sheet, trial, row):
        sheet.write(row, COL_INDEX['R'], trial.steps_value)
        sheet.write(row, COL_INDEX['N'], trial.block.N)
        sheet.write(row, COL_INDEX['S'], trial.block.S)
        sheet.write(row, COL_INDEX['V'], trial.block.V)
        

class NumberExcelExporter(ExcelExporter):
    """数量阈值数据导出"""
    
    def _write_step_fields(self, sheet, trial, row):
        sheet.write(row, COL_INDEX['N'], trial.steps_value)
        sheet.write(row, COL_INDEX['S'], trial.block.S)
        sheet.write(row, COL_INDEX['V'], trial.block.V)
    

class SizeExcelExporter(ExcelExporter):
    """尺寸阈值数据导出"""

    def _write_step_fields(self, sheet, trial, row):
        sheet.write(row, COL_INDEX['S'], trial.steps_value)
        sheet.write(row, COL_INDEX['N'], trial.block.N)
        sheet.write(row, COL_INDEX['V'], trial.block.V)


class VelocityExcelExporter(ExcelExporter):
    """动态敏感度阈值数据导出"""
    
    def _write_step_fields(self, sheet, trial, row):
        sheet.write(row, COL_INDEX['V'], trial.steps_value)
        
    
                
    
    
    
