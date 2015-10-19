#coding=utf-8
#

'''
File feature description here
'''

from django import template
from operator import itemgetter


register = template.Library()

@register.filter
def sortedByKey(dict, reverse=True):
    return sorted(dict.iteritems(), key=itemgetter(0), reverse=reverse)

