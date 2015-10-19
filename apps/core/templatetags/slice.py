#coding=utf-8
#

'''
File feature description here
'''

from django import template


register = template.Library()

@register.filter
def sliceplus(list, sliceNum, startIndex=0):
    return {'items': list[startIndex:startIndex+sliceNum], 'restNum': len(list[startIndex+sliceNum:])}
    

