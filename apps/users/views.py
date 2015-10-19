#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on Mar 21, 2014, by Junn
# 
#
from django.http.response import HttpResponse

from utils.http import Response, JResponse
from core.views import CustomAPIView
from utils.eggs import NotImplResponse
from users.models import User
from core import codes
from core.decorators import login_required_pro, debug_allowed
from core.serializers import serialize_response
from rest_framework.decorators import api_view
from utils import http

class UsersAction(CustomAPIView):
    
    @debug_allowed
    def get(self, req):
        '''所有用户'''
        return serialize_response(list(User.objects.all()))    

class UserView(CustomAPIView):
    '''
    包含接口: 
       更新某用户信息
       获取某用户信息
    '''
    
    def get(self, req, uid):
        '''get specified user info ''' 
        
        try:
            user = User.objects.get_cached(uid)
            return serialize_response(user)
        except User.DoesNotExist:
            return Response(codes.fmat('object_not_found', 'user %s' % uid))
    
    @login_required_pro
    def put(self, req, uid):
        '''update an user info'''
        
        user = req.user
        if int(uid) != user.id:
            return http.resp('permission_denied')
        
        user.update(req.DATA, new_avatar=req.FILES.get('avatar', None))
        return serialize_response(user, app_name='users')  # cast to concrete class for serializing, or exception occurred  !!!

    def delete(self, req, uid):
        return NotImplResponse(req)
        
# just for testing  
@api_view(['GET'])
def info(req):
    if req.user and req.user.is_authenticated():
        return JResponse({'user': req.user.id, 'name': req.user.nickname | req.user.username})
    #return HttpResponse({'user:': req.user, 'is_authenticated:': req.user.is_authenticated()})
    return HttpResponse('Not logined user: %s' % req.user)






