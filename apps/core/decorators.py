#coding=utf-8
import settings
from utils import http

__author__ = 'Junn'

from functools import wraps
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.core.handlers.wsgi import WSGIRequest

from utils.http import JResponse
from core import codes


def login_required(response_type='redirect', redirect_to_view=None, sign_in_redirect_msg=None):
    def _decorator(func):
        @wraps(func)
        def _wrapped_func(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated():
                if request.is_ajax():
                    context = {}
                    context.update(codes.get('login_required'))
                    return JResponse(context)
                return redirect('%s?next=%s' % (reverse('login'), request.get_full_path()))
            return func(request, *args, **kwargs)
        return _wrapped_func
    return _decorator

def debug_allowed(func):
    def _debug_allowed(obj, req, *args, **kwargs):
        if settings.DEBUG:
            return func(obj, req, *args, **kwargs)
        return http.resp('invalid_request_method')
    return _debug_allowed

def login_required_pro(func):

    def _login_required(obj, request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(obj, request, *args, **kwargs)
        return JResponse(codes.get('login_required'))
    return _login_required

def login_required_mtd(func):
    '''用于修饰method-based view请求函数. 可以找方法与login_required_pro合并'''

    def _login_required(request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(request, *args, **kwargs)
        return JResponse(codes.get('login_required'))
    return _login_required

def post_request_required(func):

    def _post_required(req, *args, **kwargs):
        if req.method == 'POST':
            return func(req, *args, **kwargs)
        return JResponse(codes.get('invalid_request_method'))
    return _post_required


def validate_id(method, key=None):
    """
    validate the id named 'key' in request method
    """
    def _validate(func):
        def validate(obj, request=None, *args, **kwargs):
            if isinstance(obj, WSGIRequest):
                # for APIView and function view
                request = obj
            if request.method != method:
                # check method
                return JResponse(codes.get('invalid_request_method'))
            if key:
                if method == "POST":
                    arg = request.POST.get(key)
                elif method == "GET":
                    arg = request.GET.get(key)
                else:
                    return JResponse(codes.get('invalid_request_method'))
                try:
                    int(arg)
                except Exception, e:
                    print e
                    return JResponse(codes.get('params_error'))
            if obj == request:
                # for APIView and function view
                return func(request, *args, **kwargs)
            return func(obj, request, *args, **kwargs)
        return validate
    return _validate


def validate_for_api(method, key=None):
    """
    for leshare api
    """
    def _validate(func):
        pass