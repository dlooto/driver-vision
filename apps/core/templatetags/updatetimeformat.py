# -*-coding:utf-8 -*
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
def updatetimeformat(d, now=None):
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

    if d.year == now.year:
        if d.month == now.month:
            if d.day == now.day:
                return d.strftime('%H:%M')
            elif d.day == now.day-1:
                return d.strftime('昨天%H:%M')
            elif d.day == now.day-2:
                return d.strftime('前天%H:%M')
            else:
                return d.strftime('%m-%d')
        else:
            return d.strftime('%m-%d')
    else:
        return d.strftime('%Y-%m-%d')
