#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on Mar 21, 2014, by Junn
# 
#

from django.db import models

from managers import BaseManager
from django.core.cache import cache


class BaseModel(models.Model):
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ['-created_time']


    def cache(self): # the object cache it-self
        cache.set(type(self).objects.make_key(self.id), self, timeout=0)    #永不过期 
                
    def clear_cache(self): # clear from cache
        cache.delete(type(self).objects.make_key(self.id))  