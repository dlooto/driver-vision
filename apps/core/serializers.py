#coding=utf-8
#
# Copyright (C) 2012-2013 FEIGR TECH Co., Ltd. All rights reserved.
# Created on 2013-8-6, by Junn
#
#
from django.utils import timezone

from rest_framework import pagination, serializers
from rest_framework.pagination import BasePaginationSerializer
from utils.http import Response
import importlib
from utils.eggs import make_instance


class BaseModelSerializer(serializers.ModelSerializer):

    created_time = serializers.SerializerMethodField('str_created_time')

    def str_created_time(self, obj):
        return obj.created_time.strftime('%Y-%m-%d %H:%M:%S')
        #return timezone.localtime(obj.created_time).strftime('%Y-%m-%d %H:%M:%S')


class HasNextField(serializers.Field):
    """
    Field that returns a boolean if there is next page of data
    """
    def to_native(self, value):
        if not value.has_next():
            return False
        return True


class CustomPaginationSerializer(pagination.BasePaginationSerializer):

    total = serializers.Field(source='paginator.count')
    has_next = HasNextField(source='*')
    #page = serializers.Field(source='number')
    #count = serializers.Field(source='paginator.per_page')

    def __init__(self, results_field_name='results', *args, **kwargs):
        """
        Override init to add in the object serializer field on-the-fly.
        """
        super(BasePaginationSerializer, self).__init__(*args, **kwargs)
        results_field = results_field_name
        object_serializer = self.opts.object_serializer_class

        context_kwarg = {}
        if 'context' in kwargs:
            context_kwarg = {'context': kwargs['context']}

        self.fields[results_field] = object_serializer(source='object_list', **context_kwarg)


def serialize_response(items, app_name=None):
    '''通用转换方法: 将数据对象列表转换成相应的serializer response对象返回
    
    @param items:    数据对象列表. 若为QuerySet结果集, 需要先转换成list对象再转入
    @param app_name: 为防止module_name被拼装成 django.serializers, 传入该参数以确保为自定义apps
    
    @return: Response object
    
    '''
    if not items: 
        return Response(items)
    
    instance = items[0] if isinstance(items, list) else items
    
    if app_name:   
        module_name = app_name + '.serializers'  # like users.serializers
    else:     
        module_name = instance.__module__.split('.')[0] + '.serializers'
        
    class_name = instance.__class__.__name__ + 'Serializer'
    return Response(make_instance(module_name, class_name, items).data)

