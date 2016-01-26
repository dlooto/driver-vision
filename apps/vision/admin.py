#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on 2015-7-8, by Junn
#

from django.contrib import admin
from vision.models import RoadModel, TrialParam, Demo, Trial, Block

from django.contrib.admin import sites
from django.views.decorators.cache import never_cache
from django.utils.text import capfirst
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import six
from django.template.response import TemplateResponse


class MyAdminSite(sites.AdminSite):
    '''为vision内models定制排序, 重写index方法'''
    
    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.module_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'perms': perms,
                        'index': capfirst(model._meta.index),    #by junn
                    }
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add', False):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'])
        
        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            
            print 'app.name: ', app['name']
            if app['name'] in ('vision', 'Vision'):
                for model in app['models']:
                    if model['name'] == 'Demos':
                        model['index'] = 0
                    if model['name'] == 'Blocks':
                        model['index'] = 1
                    if model['name'] == 'Trials':
                        model['index'] = 2
                    if model['name'] == 'Roads':
                        model['index'] = 3
                    else:
                        model['index'] = 4 
                app['models'].sort(key=lambda x: x['index'])
                print 'app.models:', app['models']         
                

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.index_template or
                                'admin/index.html', context,
                                current_app=self.name) 

# unused now
admin_site = MyAdminSite()          
        

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
    
def set_uncoming(modeladmin, request, queryset):
    queryset.update(is_coming=False)
    
     
set_is_coming.short_description = u'设为可用'
set_uncoming.short_description = u'设为不可用'
    
class TrialParamAdmin(admin.ModelAdmin):
    list_display = ('id', 'board_type', 'demo_scheme', 'move_type', 'wp_scheme',   
                    'step_scheme', 'board_size', 'road_size', 'eccent', 'init_angle', 
                    'road_marks', 'is_coming', 'trialed_count', 'created_time') # item list 
    search_fields = ('desc', )
    list_filter = ('board_type', 'demo_scheme', 'step_scheme', 'move_type', 'is_coming')
    #fields = ('board_type', 'demo_scheme', )
    ordering = ('-created_time', 'is_coming')
    actions = [set_is_coming, set_uncoming]
    change_list_template = 'admin/trial_param_list.html'   #替换template, 使转向到定制页面 

class DemoAdmin(admin.ModelAdmin):
    list_display = ('id', 'param', 'correct_rate', 'time_cost', 'is_break', 'created_time') # item list 
    search_fields = ('desc', )
    list_filter = ('is_break', )
    ordering = ('-created_time', )

class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'demo', 'tseat', 'ee', 'angle', 'cate', 'N', 'S', 'R', 'V', 'created_time') # item list 
#     search_fields = ('desc', )
    list_filter = ('cate', )
    ordering = ('-demo', )     
    
class TrialAdmin(admin.ModelAdmin):
    list_display = ('id', 'block', 'cate', 'target_road', 'resp_cost', 'is_correct', 
                    'steps_value', 'created_time') # item list 
#     search_fields = ('desc', )
    list_filter = ('is_correct', )
    #fields = ('param', 'correct_rate', 'end_time', 'is_break', 'desc')
    ordering = ('-block', ) 
    
    
admin.site.register(RoadModel, RoadAdmin)
admin.site.register(TrialParam, TrialParamAdmin)
admin.site.register(Demo, DemoAdmin)
admin.site.register(Trial, TrialAdmin)
admin.site.register(Block, BlockAdmin)
