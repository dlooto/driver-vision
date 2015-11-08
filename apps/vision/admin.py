#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on 2015-7-8, by Junn
#

from django.contrib import admin
from vision.models import RoadModel, TrialParam, Demo, Trial, Block


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
    
    
def set_is_coming(modeladmin, request, queryset):
    if len(queryset) > 1:
        raise Exception('仅可以设置一条数据 is_coming=True')
    TrialParam.objects.set_not_coming()
    queryset.update(is_coming=True)
    
     
set_is_coming.short_description = u'设为可用' 
    
class TrialParamAdmin(admin.ModelAdmin):
    list_display = ('id', 'board_type', 'demo_scheme', 'road_num', 'road_marks', 'is_coming', 'trialed_count', 'created_time') # item list 
    search_fields = ('desc', )
    list_filter = ('board_type', 'demo_scheme', 'move_type', 'is_coming')
    #fields = ('board_type', 'demo_scheme', )
    ordering = ('-created_time', 'is_coming')
    actions = [set_is_coming, ]
    change_list_template = 'admin/trial_param_list.html'   #替换template, 使转向到定制页面 

class DemoAdmin(admin.ModelAdmin):
    list_display = ('id', 'param', 'correct_rate', 'end_time', 'is_break', 'created_time') # item list 
    search_fields = ('desc', )
    list_filter = ('is_break', )
    ordering = ('-created_time', )

class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'demo', 'tseat', 'eccent', 'angle', 'cate', 'N', 'S', 'R', 'V', 'created_time') # item list 
#     search_fields = ('desc', )
    list_filter = ('cate', )
    ordering = ('-demo', )     
    
class TrialAdmin(admin.ModelAdmin):
    list_display = ('id', 'block', 'cate', 'resp_cost', 'is_correct', 'steps_value', 'created_time') # item list 
#     search_fields = ('desc', )
    list_filter = ('is_correct', )
    #fields = ('param', 'correct_rate', 'end_time', 'is_break', 'desc')
    ordering = ('-block', ) 
    
    
admin.site.register(RoadModel, RoadAdmin)
admin.site.register(TrialParam, TrialParamAdmin)
admin.site.register(Demo, DemoAdmin)
admin.site.register(Trial, TrialAdmin)
admin.site.register(Block, BlockAdmin)
