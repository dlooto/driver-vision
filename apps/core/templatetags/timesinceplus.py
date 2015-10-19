#coding=utf-8
#
import datetime
from django.utils.tzinfo import LocalTimezone
from django.utils.translation import ugettext, ungettext

'''
File feature description here
'''

from django import template


register = template.Library()

@register.filter
def timesinceplus(d, now=None):
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        if d.tzinfo:
            now = datetime.datetime.now(LocalTimezone(d))
        else:
            now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds # seconds
    
    if since <= 60:
        # d is in the future compared to now, stop processing.
        return u'刚刚'
    elif since <= 3600:
        return str(since/60) + '分钟前'
    elif since <= 86400:
        return str(since/60/60) + '小时前'
    
    if d.year == now.year:
        return d.strftime('%m-%d %H:%M')
    return d.strftime('%Y-%m-%d %H:%M')

