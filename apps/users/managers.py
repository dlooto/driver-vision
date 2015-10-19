#coding=utf-8
#
# Created on Mar 21, 2014, by Junn
# 
#

from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from utils import eggs, logs, http
from django.core.cache import cache

VALID_ATTRS = ('nickname', 'email', 'phone', 'gender', 'avatar')

def mk_key(id):
    return 'u%s' % id

class CustomUserManager(BaseUserManager):
    def _create_user(self, username, password=None, is_active=True, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username,
                          is_staff=False, is_active=is_active, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_phone(self, phone):
        try:
            return self.get(username=phone)
        except self.model.DoesNotExist:
            return None         

    def update_user(self, user, req):
        data = req.DATA
        for attr in VALID_ATTRS:  #双重循环, 以后需要改进算法
            if attr in data:
                setattr(user, attr, data.get(attr))

        user.save(using=self._db)
        return user


    def create_superuser(self, username, password, **extra_fields):
        u = self._create_user(username, password, **extra_fields)
        u.is_staff = True
        u.is_superuser = True
        u.save(using=self._db)
        return u
    
    def create_open_user(self, source_site, openid, access_token, expires_in, open_name='', avatar_url=''):
        '''创建第3方登录账号
        @param source_site:     第3方平台名称
        @param openid:          用户在第3方平台的账号id
        @param access_token:    第3方平台的访问token
        @param expires_in:      access_token的超时时间  
        @param open_name:       用户在第3方平台的昵称 
        @param avatar_url:      用户在第3方平台的头像url
        '''
        
        from auth.models import OpenAccount
        
        try:    
            ## 第3方平台注册用户不允许直接登录, 除非重置了密码(重置密码需要先绑定手机号)
            user = self._create_user( 
                username=eggs.gen_uuid1(), nickname=open_name, acct_type='O'
            )
            
            try:
                user.save_avatar(http.request_file(avatar_url))  #请求远端获取图片并保存
            except Exception, e:
                logs.err(__name__, eggs.lineno(), e)
                pass
            
            user.update_pdu(1)  #设置头像标识位
            user.update_pdu(2)  #设置昵称标识位
            user.save()
            user.cache()
            
            open_acct = OpenAccount(user=user, source_site=source_site, 
                openid=openid, access_token=access_token, expires_in=int(expires_in)
            )
            open_acct.save()
            return True, user
        except Exception, e:
            logs.err(__name__, eggs.lineno(), e)
            return False, u'账号绑定异常'
        

    ############################################################   cache methods
    def cache_all(self):    #TODO: abstract these cache_xxx method into base class ...
        users = self.all()
        for u in users:
            u.cache()
            
        logs.info('====================================> All user entities cached.')   
    
    def get_cached(self, uid): #TODO: using cache later...
        '''return cached user object'''
        user = cache.get(mk_key(uid))
        if not user:
            try:
                user = self.get(id=int(uid))
                user.cache()
            except self.model.DoesNotExist:
                logs.err(__name__, eggs.lineno(), 'User not found: %s' % uid)
                return None
            except Exception, e:
                logs.err(__name__, eggs.lineno(), 'get_cached user error: %s' % e)
                return None
            
        return user    
        
    
    
    