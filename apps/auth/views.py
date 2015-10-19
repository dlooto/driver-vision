#coding=utf-8
#
# Created on 2015/8/14, by Junn
# 
#
from django.contrib.auth import logout as system_logout 
from utils.http import standard_response
from core.views import CustomAPIView
from users.forms import UserLoginForm
from utils import http, logs
from core.serializers import serialize_response
from rest_framework.decorators import api_view


class LoginAction(CustomAPIView):

    def get(self, req):
        # TODO: if is login, need to redirect here
        return standard_response('test.html', req, {'form': UserLoginForm})

    def post(self, req):
        form = UserLoginForm(req, data=req.POST)
        if form.is_valid():
            user = form.login(req)
            response = serialize_response(user)
            
            #token = user.get_authtoken()
            #if not token:
            #    return http.resp('authtoken_error', 'Auth error')
            
            #response.set_cookie('authtoken', token)
            return response
        else:
            if form.error_status == 'passwd_set_required':  #被邀请用户首次登录, 或用户未设置密码
                return http.resp('passwd_set_required')
            
            logs.error('form error: \n %s' % form.errors)
            if form.error_status == 'inactive':
                return http.failed('您的帐号已暂停使用')
            
            return http.failed('用户名或密码错误')
            

@api_view(['POST'])        
def logout(req):
    if req.user.is_authenticated():
        system_logout(req)
        return http.ok()
    return http.failed('退出失败')


