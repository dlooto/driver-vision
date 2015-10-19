#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on 2014-4-24, by junn

#

############################################################
##         日志信息配置 
############################################################


import os

LOG_ROOT = os.path.join(os.path.dirname(__file__), '../../logs')

LOG_FILE_PATH = os.path.join(LOG_ROOT, "vision.log")

# 日志显示级别
LOG_LEVEL = 'INFO'  #ERROR, INFO, DEBUG, WARN

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(pathname)s:%(lineno)s] %(message)s",
            'datefmt' : "%Y/%m/%d %H:%M:%S"
        },
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'file': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'maxBytes': 5*1024*1024,
            'backupCount': 20,
            'formatter': 'standard',
        },
        'mail_admins': {  
            'level': 'ERROR',  
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',  
            'include_html': True,  
        },  
        'console':{
            'level': LOG_LEVEL,
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console','file'], # 同时写到console和文件里
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'vision': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'jpush': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',          
        },
                        
    }
}


