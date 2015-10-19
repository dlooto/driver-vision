#coding=utf-8
#

'''
File feature description here
'''

from django import template


register = template.Library()

@register.filter
def split(value, arg=' '):
    if value:
        return [ item.strip() for item in value.split(arg) ]
    return []

