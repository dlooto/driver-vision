#coding=utf-8
#
# Created on 2013-8-7, by Junn
#
#
import uuid
import random
import string
from math import sin, asin, cos, radians, fabs, sqrt

from django.core.paginator import Paginator, EmptyPage, Page
from http import Response
import re
import hashlib
import importlib
import time


# 用于求字符串长度，中文汉字计算为两个英文字母长度
ecode = lambda s: s.encode('gb18030')

DEFAULT_PAGE_SIZE = 10

def page_instances(instances, count=DEFAULT_PAGE_SIZE, page=1):
    '''
    page instances, return empty list if there is no instances in one page
    @param count: the max-num of paged instances per-page, default 20
    @param page: the page num which to looking for
    '''
    try:
        if int(count) < 1 or int(page) < 1:
            raise ValueError
    except ValueError:
        return None
    paginator = Paginator(instances, count)
    try:
        result = paginator.page(page)
    except EmptyPage:
        result = Page([], 0, paginator)

    return result

def handle_paging(request, objects):
    '''处理分页请求, 返回分页后的数据列表
    @param request: 请求对象
    @param objects: objects为数据对象列表'''
    
    return page_instances(objects, 
        request.GET.get('count', DEFAULT_PAGE_SIZE), 
        request.GET.get('page', 1)
    )            
        

def gen_uuid():
    return str(uuid.uuid1())

def gen_uuid1():
    '''gen_uuid生成规则基础上去掉所有横扛'''
    return gen_uuid().replace('-', '')

def rename_file(file, file_name=''): 
    """
    rename user uploaded file with uuid or given file name, return renamed file
    file:   request.FILES中获取的数据对象
    """
    suffix = '.' + file.name.split('.')[-1]
    file.name = (file_name or gen_uuid()) + suffix
    return file

phone_format = r'^((\+86)|(86)|(086))?1[34578]\d{9}$'  #r'^1[3458]\d{9}$'
MOBILE_PHONE_COMPILE = re.compile(phone_format)
def is_phone_valid(phone):
    return True if phone and MOBILE_PHONE_COMPILE.match(phone) else False

def normalize_phone(phone):
    '''手机号规范化处理, 截取后面11位返回, 如将+8615982231010转为15982231010, 即去掉号码前的86|086|+86等
    '''
    phone = ''.join(phone).strip()
    if phone[0] != '+' and len(phone) == 11:
        return phone
    if len(phone) <= 11:
        return phone
    return phone[-11:] #从倒数11位起取到尾部

def random_num(length=6):
    """
    根据传入的length长度, 随机生成对应长度的数字字符串
    """
    a = string.digits * (length / 10 + 1)
    return ''.join(random.sample(a, length))

def make_sig(s, secret_key, offset=''):
    '''算法: 根据字符串及密钥, 进行加密生成签名'''
    return hashlib.md5('%s%s_%s' % (s, secret_key, offset)).hexdigest().upper()

def hav(theta):
    s = sin(theta / 2)
    return s * s


EARTH_RADIUS = 6371  # 地球平均半径，6371km


def cal_dist(lat0, lng0, lat1, lng1, radius=None, decimal=2):
    """
    计算两坐标点之间距离(Km)
    当传入可选参数radius时同时判断其中一点是否在: 以另一点为中心, radius为半径的圆形范围内
    @param lat0: 第一个点的纬度
    @param lng0: 第一个点的经度
    @param lat1: 第二个点的纬度
    @param lng1: 第二个点的经度
    @param radius: 半径(Km)
    """
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)
    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))
    if not radius:
        return float(('%%.%df' % decimal) % distance)
    if distance <= radius:
        is_in = True
    else:
        is_in = False
    return is_in, float(('%%.%df' % decimal) % distance)


def timesince(start_time, end_time, default="1天"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    diff = end_time - start_time
    if end_time > start_time:
        periods = (
            (diff.days / 365, "年"),
            (diff.days / 30, "个月"),
#            (diff.days / 7, "周"),
            (diff.days, "天"),
#            (diff.seconds / 3600, "小时"),
#            (diff.seconds / 60, "分钟"),
#            (diff.seconds, "秒"),
        )
        for period, unit in periods:
            if period:
                return "%d%s" % (period, unit)

    return default

def str_to_time(timestr, format='%Y-%m-%d %H:%M:%S'):
    '''将时间字符串转为对应的时间对象'''
    return time.strptime(timestr, format)


def make_instance(module_name, class_name, *args, **kwargs):
    '''build instance by module_name and class name passed
    
    examples:
        x = make_instance("users.models", "Family", 0, 4, disc="bust")
    '''
    try:
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_(*args, **kwargs)
    except NameError, e:
        raise NameError("Module %s or class %s is not defined" % (module_name, class_name))
    except Exception, e:
        raise e  
    
def NotImplResponse(*args, **kwargs):
    return Response('Not Implemented')

import inspect
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

