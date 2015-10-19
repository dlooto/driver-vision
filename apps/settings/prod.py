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
    'vt.dondon.im',    
    '127.0.0.1', 
]

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.mysql', # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": 'vision',                 # Or path to database file if using sqlite3.
        "USER": 'root',                       # Not used with sqlite3.
        "PASSWORD": 'Nian2014@n',                 # Not used with sqlite3.
        "HOST": 'localhost',                  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": '3306',                       # Set to empty string for default. Not used with sqlite3.
    }
}


MIDDLEWARE_CLASSES += [
    #'core.middleware.PrintSqlMiddleware',
    #'core.middleware.PrintRequestParamsMiddleware',
    
]

MEDIA_URL = 'http://vt.dondon.im/media/'
STATIC_URL = 'http://vt.dondon.im/static/'

INSTALLED_APPS += ['gunicorn',]

ADMINS = (

)

MANAGERS = ADMINS



