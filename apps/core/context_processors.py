#coding=utf8

from django.conf import settings

def import_settings(req):
    '''载入常量设置'''
    
    return {
        'MAP_API_CODE': settings.MAP_API_CODE, 
        
    }

