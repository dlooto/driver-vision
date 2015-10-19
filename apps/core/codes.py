#coding=utf-8
#
# Created on Mar 21, 2014, by Junn
#

'''
错误说明: 
    code-00403, 前2位为错误码类别, 后3位为错误码. 其中:
    
    00: 系统类型
    10: 业务通用类型
    20: 用户模块类型
    
    ...

'''

CODE = {

    # system code
    'parse_error':              {'code': 90400, 'msg': "malformed request."},
    'authentication_failed':    {'code': 90401, 'msg': "incorrect authentication credentials."},
    'csrf_invalid':             {'code': 90403, 'msg': "csrftoken invalid, refresh and set it from the cookies."},
    'not_found':                {'code': 90404, 'msg': "request not found"},
    'invalid_request_method':   {'code': 90405, 'msg': "method not allowed"},
    'not_acceptable':           {'code': 90406, 'msg': "could not satisfy the request's Accept header"},
    'unsupported_media_type':   {'code': 90415, 'msg': "unsupported media type in request."},
    'throttled':                {'code': 90429, 'msg': "request was throttled."},
    'not_authenticated':        {'code': 90600, 'msg': "authentication credentials were not provided."},
    'permission_denied':        {'code': 90601, 'msg': "no permission to perform this action."},
    'unauthed_client':          {'code': 90602, 'msg': "Client not authenticated ."},
    'authtoken_error':          {'code': 90603, 'msg': "get auth_token error ."},
    
    
    # common code
    'ok':                       {'code': 1, 'msg': "ok"},
    'failed':                   {'code': 0, 'msg': "failed. "},
    
    'invalid_page_or_count':    {'code': 10004, 'msg': "invalid page or count"},
    'params_error':             {'code': 10005, 'msg': "parameters input error {0}"},
    'object_not_found':         {'code': 10006, 'msg': "object not found {0}"},
    'operate_duplicate':        {'code': 10008, 'msg': "duplicate operation {0}"},
    'form_errors':              {'code': 10009, 'msg': "form errors {0}"},
    'server_error':             {'code': 10010, 'msg': "server errors"},

    # user code
    'login_required':           {'code': 20001, 'msg': "login required"},
    'duplicate_signup':         {'code': 20002, 'msg': "you can register only one account on one device"}, 
    'passwd_set_required':      {'code': 20003, 'msg': "The password is need to set for account security"},   
    'code_invalid':             {'code': 20004, 'msg': "sms code invalid or expired"},
    'bind_failed':              {'code': 20005, 'msg': "mobile binding failed"},

    # device code
    'have_no_device':           {'code': 30005, 'msg': "no any device"},

    # 
}

def get(crr):
    '''返回错误码常量'''
    return CODE[crr]

def got(crr):
    '''返回错误码常量, 以变量形式重新复制一份'''
    r = CODE[crr]
    return r.copy()
    

def fmat(crr, msg):
    '''格式化错误码, 如{'code': 10001, 'msg': "failed."} 格式化后将变成
    {'code': '10001', 'msg': "failed. 参数错误"}
    '''
    if not msg:
        return get(crr)
    
    result = got(crr)
    result['msg'] = '%s%s' % (result['msg'], msg)
    return result

def append(crr, _dict):
    '''在已有错误码内添加新的返回参数.
    如: 
     往  {'code': 10001, 'msg': "failed"} 里添加 {'name': 'hello'}, 则返回结果为
        {'code': 10001, 'msg': "failed", 'name': 'hello'}
    '''
    rc = got(crr)
    rc.update(_dict)
    return rc