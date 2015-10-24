#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Oct 19, 2015, by Junn
#
from utils import http, logs
from vision import gui
from config import *


def new_demo(req):
    '''创建新的试验. 管理者请求该方法
    管理者参数设置完毕, 并点击确认后请求该方法
    ''' 
    
    
    demo = new_demo()
    demo.gen_board()
    req.session['demo'] = demo
    
    return http.ok('创建试验成功')
    
def start_demo(req):
    '''开始试验
    被试者点击开始时, 请求该方法
    '''

    demo = req.session.get('demo')
    if demo:
        logs.info('demo starting...')
         
        ## 进入到测试界面, 启动一个1.6s的trial. 一直到所有的trial完成
        demo.start()
         
        logs.info('demo ended with ')
        del req.session['demo']
        return http.ok('试验完成')
    
    return http.failed('参数未设置')    
        