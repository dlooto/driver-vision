#coding=utf-8
#
from django.utils.safestring import mark_safe

'''
File feature description here
'''

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import urlize as urlize_impl

register = template.Library()

@register.filter
@stringfilter
def urlizeplus(value, autoescape=None):
    """Converts URLs in plain text into clickable links."""
    return mark_safe(urlize_impl(value, nofollow=True, autoescape=autoescape).replace('<a', '<a target="_blank"'))