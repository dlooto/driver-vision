#coding=utf-8
#
# Copyright (C) 2014  NianNian TECH Co., Ltd. All rights reserved.
# Created on Jan 4, 2016, by Junn
#
# from celery.task import task
# 
# @task
# def start_move(worker):
#     if worker.is_working:
#         return
#     worker.is_working = True
#     worker.run()
        
# @task()
# def stop_move(worker):
#     print 'worker:', worker.is_working
#     if not worker.is_working:
#         return
#     worker.is_working = False

from vision.motion import MotionWorker
import time

def foo():
    for i in range(1146880):
        MotionWorker(None, None, None).start()
        #time.sleep()
        print i
    
    