#coding=utf-8
#
# Copyright (C) 2012-2013 FEIGR TECH Co., Ltd. All rights reserved.
# Created on 2014-4-6, by Junn
#
#

############################################################
##         生产环境参数配置 
############################################################

import os

from base import *

ALLOWED_HOSTS = [
    'mombaby.me',
    'www.mombaby.me',
    'm1.mombaby.me', 
    'dr.mombaby.me', 
    'shop.mombaby.me',
    'dl.mombaby.me',
    'api.mombaby.me',
    'admin.mombaby.me',
    
    '127.0.0.1', 
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/etc/mysql/my.cnf',
        }, 
    }
}

MIDDLEWARE_CLASSES += [
    #'core.middleware.PrintSqlMiddleware',
    #'core.middleware.PrintRequestParamsMiddleware',
    
]

MEDIA_URL = 'http://m1.mombaby.me/media/'
STATIC_URL = 'http://m1.mombaby.me/static/'

INSTALLED_APPS += ['gunicorn',]

ADMINS = (

)

MANAGERS = ADMINS



