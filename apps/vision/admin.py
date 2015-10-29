#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on 2015-7-8, by Junn
#

from django.contrib import admin
from vision.models import Road, TrialParam


def make_valid(modeladmin, request, queryset):
    queryset.update(is_valid=True) 
     
def make_unvalid(modeladmin, request, queryset):
    queryset.update(is_valid=False)   

     
make_valid.short_description = u'set 有效' 
make_unvalid.short_description = u'set 无效'

        
class RoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_real', 'is_valid', 'created_time') # item list 
    search_fields = ('name', )
    list_filter = ('is_real', 'is_valid',)
    fields = ('name', 'is_real', )
    ordering = ('created_time', )
    actions = [make_valid, make_unvalid]
    
def set_trialed(modeladmin, request, queryset):
    queryset.update(is_trialed=True) 
     
def set_not_trialed(modeladmin, request, queryset):
    queryset.update(is_trialed=False)   

     
set_trialed.short_description = u'set 已执行' 
set_not_trialed.short_description = u'set 未执行'    
    
class TrialParamAdmin(admin.ModelAdmin):
    list_display = ('id', 'board_type', 'demo_scheme', 'road_num', 'road_marks', 'eccent', 'is_trialed', 'created_time') # item list 
    search_fields = ('desc', )
    list_filter = ('board_type', 'demo_scheme', 'move_type', 'is_trialed')
    #fields = ('board_type', 'demo_scheme', )
    ordering = ('-created_time', )
    actions = [set_trialed, set_not_trialed]    

admin.site.register(Road, RoadAdmin)
admin.site.register(TrialParam, TrialParamAdmin)
