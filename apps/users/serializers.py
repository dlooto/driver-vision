#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on 2014-9-9, by Junn
# 
#

from core.serializers import BaseModelSerializer, CustomPaginationSerializer
from users.models import User
from rest_framework import serializers
import settings


class UserSerializer(BaseModelSerializer):
    avatar = serializers.SerializerMethodField('get_avatar')
    #birth = serializers.SerializerMethodField('get_birth')
    info_completed = serializers.SerializerMethodField('is_info_completed')  #资料是否完整

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'email', 'phone', 
                  'gender', 'avatar', 'birth', 'info_completed', 'acct_type', 'login_count'
        )
        
    def get_birth(self, obj):
        return obj.birth.strftime('%Y-%m-%d')
        
    def get_avatar(self, obj):
        return '%s%s/%s' % (settings.MEDIA_URL,settings.USER_AVATAR_DIR['thumb'], obj.avatar) if obj.avatar else ''  
    
    def is_info_completed(self, obj):
        return 0 if obj.pdu[2] == '0' else 1

class PagingUserSerializer(CustomPaginationSerializer):

    class Meta:
        object_serializer_class = UserSerializer
        
        
