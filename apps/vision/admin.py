#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on 2015-7-8, by Junn
#

from django.contrib import admin
from vision.models import Road


def make_valid(modeladmin, request, queryset):
    queryset.update(is_valid=True) 
     
def make_unvalid(modeladmin, request, queryset):
    queryset.update(is_valid=False)   

     
make_valid.short_description = u'设置为有效' 
make_unvalid.short_description = u'设置为无效'

        
class RoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_real', 'is_valid', 'created_time') # item list 
    search_fields = ('name', )
    list_filter = ('is_real', 'is_valid',)
    fields = ('name', 'is_real', )
    ordering = ('created_time', )
    actions = [make_valid, make_unvalid]

admin.site.register(Road, RoadAdmin)
