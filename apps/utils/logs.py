#coding=utf-8
#
# Created on Apr 24, 2014, by Junn
# 
#

'''
日志系统
''' 

import logging
logger = logging.getLogger("vision")


def info(msg, *args, **kwargs):
    logger.info('%s' % msg, *args, **kwargs)
    
def debug(msg, *args, **kwargs):
    logger.debug('%s' % msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error('%s' % msg, *args, **kwargs)
    
def warn(msg, *args, **kwargs):
    logger.warn('%s' % msg, *args, **kwargs)

## 打印输出模块名和代码行号
def inf(module_name, line_no, msg, *args, **kwargs):
    logger.info('%s:%s \n %s' % (module_name, line_no, msg), *args, **kwargs)  

def deb(module_name, line_no, msg, *args, **kwargs):
    logger.debug('%s:%s \n %s' % (module_name, line_no, msg), *args, **kwargs) 
        
def err(module_name, line_no, msg, *args, **kwargs):
    '''打印输出模块名和代码行号,'''
    logger.error('%s:%s \n %s' % (module_name, line_no, msg), *args, **kwargs)     
    
def war(module_name, line_no, msg, *args, **kwargs):
    '''打印输出模块名和代码行号,'''
    logger.warn('%s:%s \n %s' % (module_name, line_no, msg), *args, **kwargs) 