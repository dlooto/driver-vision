#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on Mar 21, 2014, by Junn
# 
#

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

import settings
from managers import CustomUserManager
from core.models import BaseModel
from django.core.cache import cache
from django.contrib.auth import login


GENDER_CHOICES = (
    ('M', u'Male'), 
    ('F', u'Female'),
    ('U', u'Unknown'),
)

ACCT_TYPE_CHOICES = (
    ('E', u'显式注册'),   #正常流程注册
    ('I', u'邀请注册'),   #被邀请形式隐式注册
    ('O', u'第3方登录注册') 
)

VALID_ATTRS = ('phone', 'nickname', 'gender', 'birth', 'email')

def mk_key(id):
    return 'u%s' % id

# 用户资料各项信息的修改位
DEFAULT_PDU = '100000'
PDU_ITEMS = {
    'phone':        0,   
    'avatar':       1, 
    'nickname':     2,
    'innername':    3,
    'birth':        4,
    'gender':       5        
}


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(u'用户名', max_length=255, unique=True)
    phone = models.CharField(u'手机号', max_length=18, blank=True, null=True, default='')
    email = models.EmailField('Email', blank=True, null=True, default='')

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(u'注册时间', auto_now_add=True)
    acct_type = models.CharField(u'账号类型', max_length=1, choices=ACCT_TYPE_CHOICES, default='E')

    nickname = models.CharField(u'昵称', max_length=32, null=True, blank=True, default='')
    gender = models.CharField(u'性别', max_length=1, choices=GENDER_CHOICES, default='U')
    
    # 该字段仅存储文件名(不包括路径), 大图小图同名且以不同的路径区分
    avatar = models.CharField(u'头像', max_length=80, blank=True, null=True, default=settings.USER_DEFAULT_AVATAR)
    
    birth = models.DateField(u'生日', null=True, blank=True, auto_now_add=True)
    
    # 个人资料完成度标识, 0位表示未填写, 1位表示已填
    # 各位置从左到右依次为: phone, avatar, nickname, innername, birth, gender
    pdu = models.CharField(max_length=10, default=DEFAULT_PDU)
    
    login_count = models.IntegerField(u'登录次数', default=0)
    
    last_login_ip = models.IPAddressField(u'最后登录IP', null=True, blank=True)

    USERNAME_FIELD = 'username'
    backend = 'django.contrib.auth.backends.ModelBackend'

    objects = CustomUserManager()

    def __unicode__(self):
        return self.nickname if self.nickname else self.username

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
        app_label = 'users'
        swappable = 'AUTH_USER_MODEL'
        
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        
    def update(self, data, new_avatar=None):
        return self
        
    def cache(self):
        cache.set(mk_key(self.id), self, timeout=0)    #永不过期 
                
    def clear_cache(self):
        cache.delete(mk_key(self.id)) #TODO: maybe put this into baseModel   
        
    def save_avatar(self, avatar_file):
        pass
        
    def get_avatar_path(self): #返回头像全路径 
        if not self.avatar:
            return ''
        return '%s%s/%s' % (settings.MEDIA_URL, settings.USER_AVATAR_DIR['thumb'], self.avatar)             
                
        
    def post_login(self, req):   
        '''登录及后续其他处理. 
        @param req: django request请求对象'''
         
        login(req, self)

        if 'HTTP_X_FORWARDED_FOR' in req.META.keys():
            self.last_login_ip = req.META['HTTP_X_FORWARDED_FOR']
        else:
            self.last_login_ip = req.META['REMOTE_ADDR']
        
        self.incr_login_count()    #登录次数+1
        self.save()  
        self.cache()      
            
#     def get_authtoken(self):
#         '''返回登录鉴权token'''
#         
#         try:
#             token, created = Token.objects.get_or_create(user=self)
#             return token.key if token else ''
#         except Exception, e:
#             logs.error('get auth_token error \n % s' % e)
#             return ''
        
    def is_invited_first_login(self):
        '''是否被亲友邀请注册用户首次手机号登录'''   
        if not self.is_active and self.is_invited_signup():
            return True
        return False
    
                  
#     def save_thumb(self, thumb_size):
#         if not self.avatar:
#             return
#          
#         DJANGO_TYPE = self.avatar.file.content_type
#             
#         image = Image.open(StringIO(self.avatar.read()))
#         image.thumbnail(thumb_size, Image.ANTIALIAS)
#          
#         # save the thumbnail to memory
#         temp_handle = StringIO()
#         image.save(temp_handle, 'png')
#         temp_handle.seek(0) # rewind the file
#          
#         # save to the thumbnail field
#         suf = SimpleUploadedFile(os.path.split(self.avatar.name)[-1], temp_handle.read(), content_type=DJANGO_TYPE)
#         self.thumb.save(self.avatar.name, suf, save=False)
              
    def is_invited_signup(self):
        return True if self.acct_type == 'I' else False    
    
    def get_short_name(self):
        return self.nickname if self.nickname else self.username

    def get_username(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_bound_user(self):
        if self.bound_uid:
            return User.objects.get(id=self.bound_uid)
        return self
    
    def update_pdu(self, index):
        '''更新个人资料完成度.
        一旦填写某项资料, 则设置完成度标识位为1(未设置时为0), index表示位置序号,从0开始
        '''
        if self.pdu[index] == '1':
            return
        ps = list(self.pdu)
        ps[index] = '1'
        self.pdu = ''.join(ps)

    ############################################################
    
    def incr_login_count(self):
        '''登录次数加1'''
        self.login_count += 1
        
    def is_invited_signup_passwd_set_required(self):
        return True if self.is_invited_signup() and not self.is_active else False
    

class Profile(BaseModel):
    user = models.ForeignKey('users.User', verbose_name=u'用户')
    #city = models.CharField(u'城市', max_length=20, null=True)
    address = models.CharField(u'地址', max_length=50, null=True)
    
    def __unicode__(self):
        return self.id
    
    class Meta:
        verbose_name = u'用户详情'
        verbose_name_plural = u'用户详情'
    

class PasswordResetRecord(BaseModel):
    user = models.ForeignKey(User, verbose_name=u'用户')
    key = models.CharField(u'重置密码验证码', max_length=100)
    is_valid = models.BooleanField(u'是否可用', default=True)

    def __unicode__(self):
        return "%s, %s, %s" % (self.user, self.key, self.is_valid)

    class Meta:
        verbose_name = u'重置密码的验证码'
        verbose_name_plural = u'重置密码的验证码'


class MobileBindingRecord(BaseModel):
    user = models.ForeignKey(User, verbose_name=u'用户')
    mobile = models.CharField(u'电话号码', max_length=16)
    bound = models.BooleanField(u'是否绑定', default=True)

    def __unicode__(self):
        return "%s, %s" % (self.user, self.mobile)

    class Meta:
        verbose_name = u'手机绑定记录'
        verbose_name_plural = u'手机绑定记录'
