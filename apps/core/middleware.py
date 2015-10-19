#coding=utf-8

from django.middleware.csrf import get_token
from utils import logs, http
from auth.models import get_authed_client


from django.db import connection
from utils import eggs
from django.http.response import HttpResponse


class PrintSqlMiddleware(object):

    def process_response(self, request, serialize_response):
        logs.info('Agent: %s' % request.META.get('HTTP_USER_AGENT'))
        for sql in connection.queries:
            logs.info('[DEBUG-SQL]%s;   time: %s' % (sql['sql'], sql['time']))
        return serialize_response


class GetTokenMiddleware(object):

    def process_response(self, request, response):
        if request.method in ("POST", "PUT", "DELETE"):
            get_token(request)
        return response
    
class AuthedClientMiddleware(object):
    '''验证授权的客户端请求, 不允许非授权的client请求服务端api'''
    
    def process_request(self, request):
        return None
    
    def process_view(self, req, view, view_args, view_kwargs):
        '''添加访中间件方法, 则每个请求需要额外添加查询参数client_key和sig, 请求示例:
        http://api.abc.com/v1/users/1?client_key=xxxx&sig=xxxxx&other_param=xxxx
        
        注: 
        后续扩展点: 除web外, 但凡api形式的形式, 都必须检查client_key和sig参数. 
        可考虑将api服务部署到单独的机器上, 尤其当api需要对其他授权第3方开放时. 
        
        '''
        client_key = req.REQUEST.get('client_key', '')
        
        client = get_authed_client(client_key)
        if not client or not _check_sig(req, client):
            return http.resp('unauthed_client')
        
        # Enter into view_func for next processing
        return None 
                
                
OFFSET_CONST = '0yp*wsx90oyt90n'
                
def _check_sig(req, client):
    """
    path = /v1/auth/login?client_key=xxx&sig=xxxxxx
    sig = md5(path+SALT)
    """
    param_sig = req.REQUEST.get('sig')
    if not param_sig:
        return False
    path = req.get_full_path()
    path = path.replace('&sig=%s' % param_sig, '').replace('sig=%s&' % param_sig, '').replace('sig=%s' % param_sig, '')
    return True if eggs.make_sig(path, client.secret_key, offset=OFFSET_CONST) == param_sig else False                
                
class GetAuthSigMiddleware(object):
    '''Used for testing...'''
    
    def process_request(self, request):
        '''为便于API本地接口测试, 添加该中间件函数. 仅在测试环境下使用'''
        get_sig = request.REQUEST.get('get_sig')
        client_key = request.REQUEST.get('client_key')
        if not get_sig or get_sig != 'true' or not client_key:
            return None
        
        client = get_authed_client(client_key)
        if not client:
            return HttpResponse('client not found with key: %s' % client_key)
        
        tmp_path = request.get_full_path()
        print 'tmp_path:', tmp_path
        path = tmp_path.replace('&get_sig=true', '').replace('get_sig=true&', '').replace('get_sig=true', '')
        print 'path:', path
        print request.META['HTTP_HOST']
        return HttpResponse(eggs.make_sig(path, client.secret_key, offset=OFFSET_CONST))          
                

class PrintRequestParamsMiddleware(object):
    '''Add this middleware for printing request params when api requesting'''

    def process_request(self, request):
        logs.debug('')
        logs.debug('------------------ Request Params pre-view ------------------ begin')
        logs.debug('%s %s' % (request.method, request.path))
        logs.debug('Params: %s' % request.REQUEST)
        logs.debug('Http User Agent: %s' % request.META.get('HTTP_USER_AGENT', None))
        
        # only for testing, remove when online
        #client = get_authedapp(app_key=request.REQUEST.get('app_key', ''))
        #if not client:
        #    return
        #logs.info('sig: %s' % eggs.make_sig(request.get_full_path(), client.secret_key))
        
        #logs.info('FILES: %s' % request.FILES)
        logs.debug('------------------ Request Params pre-view  ----------------- end')
        logs.debug('')
        
        return None
