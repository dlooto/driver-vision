#coding=utf-8

# Created by Junn

from django.db.models import Manager, Q
from django.db import connection
from django.core.cache import cache
from utils import logs, eggs

def execute_raw_sql(sql):
    """
    @param sql:需要执行的sql语句
    @summary: 对自定义的sql语句进行执行
    """
    data_cursor = connection.cursor()
    data_cursor.execute(sql)


class BaseManager(Manager):
    def __init__(self):
        super(BaseManager, self).__init__()

    def query_for_list(self, sql, meta=None, args=None):
        """
        @param sql:查询的sql语句
        @param meta:需要进行映射的map的key(必须和sql语句中的字段顺序一致)
        @return: 返回的data中的每一项为map
        """
        data_cursor = connection.cursor()
        if args:
            data_cursor.execute(sql, args)
        else:
            data_cursor.execute(sql)
        data = []
        result = data_cursor.fetchall()
        if result:
            if isinstance(meta, dict):
                keys = meta.keys()

                for row in result:
                    row_map = {}
                    i = 0
                    for key in keys:
                        row_map[meta[key]] = unicode(row[i])
                        i += 1
                    data.append(row_map)
            elif isinstance(meta, (list, tuple)):
                for row in result:
                    row_map = {}
                    i = 0
                    for key in meta:
                        row_map[key] = unicode(row[i]) if row[i] != None else ''
                        i += 1
                    data.append(row_map)
            else:
                data = result
        return data

    def execute_sql(self, sql):
        """
        @param sql:需要执行的sql语句
        @summary: 对自定义的sql语句进行执行
        """
        execute_raw_sql(sql)

    def get_by_id(self, obj_id, q=None):
        q = q & Q(id=obj_id) if q else Q(id=obj_id)
        try:
            return self.get(q)
        except Exception, e:
            logs.error('%s' % e)
            return None

    def get_obj(self, q):
        try:
            return self.get(q)
        except Exception, e:
            logs.error('' + e)
            return self.filter(q)[0] if self.filter(q) else None

    ############################################################   cache methods
    def make_key(self, obj_id):
        '''现有key生成规则, 需要确保整个工程中所有模型不能同名!!! '''
        return u'%s%s' % (self.model.__name__, obj_id)
    
    def cache_all(self):
        '''数据量大以后, 需要考虑将数据批量缓存'''   
        objs = self.all()
        for obj in objs:
            obj.cache()
            
        logs.info('====================================> All %s objects cached.' % self.model.__name__)   
    
    def get_cached(self, obj_id):
        '''获取单个的缓存数据对象'''
        obj = cache.get(self.make_key(obj_id))
        if not obj:
            try:
                obj = self.get(id=int(obj_id))
                obj.cache()
            except self.model.DoesNotExist:
                logs.err(__name__, eggs.lineno(), 'Object not found: %s %s' % (self.model.__name__, obj_id))
                return None
            except Exception, e:
                logs.err(__name__, eggs.lineno(), 'get_cached object error: %s' % e)
                return None
            
        return obj
    
    def get_cached_many(self, **kwargs):
        pass
    
  
