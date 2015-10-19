#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on Mar 21, 2014, by Junn
# 
#

import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from models import User


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput, required=False)   #required=False, 为定制错误消息
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."),
        required=False)

    class Meta:
        model = User
        fields = ("username",)
        
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not PASSWORD_COMPILE.match(password1):
            self.error_status = 2
            raise forms.ValidationError(u"密码只能为6-16位英文字符或下划线组合。")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.phone = self.cleaned_data.get("username")
        if commit:
            user.save()
            #user.cache()
        return user

PASSWORD_COMPILE = re.compile(r'^\w{6,16}$')
MOBILE_PHONE_COMPILE = re.compile(r'^1[3458]\d{9}$')

class UserSignupForm(UserCreationForm):
    """
    for user signup
    username must be a mobile phone number
    """
    username = forms.RegexField(max_length=11, regex=r'^1[3458]\d{9}$',
                                error_message=u'请输入有效的手机号码。')
    
    def __init__(self, *args, **kwargs):
        # 为了精确提示错误信息, 添加该属性  
        # 1-用户已存在, 2-密码格式错误,  
        self.error_status = 1       # 默认用户已存在
        super(UserSignupForm, self).__init__(*args, **kwargs)  
    
    
class UserLoginForm(AuthenticationForm):
    """
    以注册的手机号进行登录. 后期可进行扩展, 以绑定email和用户名
    """

    def __init__(self, request=None, *args, **kwargs):
        self.error_status = 'invalid_login'  #used for API-calling error promotion exactly 
        super(UserLoginForm, self).__init__(*args, **kwargs) 

    error_messages = {
        'invalid_login': u"请输入正确的手机号和密码。",
        'inactive': u"您的帐号已暂停使用。",
        'passwd_set_required': u"需要设置登录密码",
    }

    def clean(self):
        '''重载父类方法'''
        
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username:
            try:
                user = User.objects.get(username=username)
                if not user.has_usable_password():
                    self.error_status = 'passwd_set_required'
                    raise forms.ValidationError(self.error_messages['passwd_set_required'])
            except User.DoesNotExist:
                raise forms.ValidationError(self.error_messages['invalid_login'])

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
            
            #如果是被邀请注册用户首次登录, 或者无有效密码(第3方账号登录用户首次用手机号登录) 
            elif self.user_cache.is_invited_first_login(): 
                self.error_status = 'passwd_set_required'
                raise forms.ValidationError(self.error_messages['passwd_set_required'])
            elif not self.user_cache.is_active:    
                self.error_status = 'inactive'
                raise forms.ValidationError(self.error_messages['inactive'])
        else:
            raise forms.ValidationError(self.error_messages['invalid_login'])
        return self.cleaned_data
    
    def login(self, req):
        user = self.get_user()
        user.post_login(req)
        return user

class UserChangeForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not PASSWORD_COMPILE.match(password1):
            raise forms.ValidationError(u"密码只能为6-16位英文字符或下划线组合。")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(forms.Form):
    """
    
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput, required=False)

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError(u'密码输入不正确。')
        return password

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not PASSWORD_COMPILE.match(password1):
            raise forms.ValidationError(u"密码只能为6-16位英文字符或下划线组合。")
        if password1 == self.cleaned_data.get('password'):
            raise forms.ValidationError(u"新旧密码不能相同。")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u"新密码和重复密码不一致。")
        return password2
    
    def set_password(self):
        self.user.set_password(self.cleaned_data.get('password1'))
        self.user.save()


class PasswordResetForm(forms.Form):
    """
    for user reset the password
    """
    password1 = forms.CharField(label=_(u'Password'),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput, required=False)

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not PASSWORD_COMPILE.match(password1):
            raise forms.ValidationError(u"密码只能为6-16位英文字符或下划线组合。")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

    def reset(self):
        user = self.user
        user.set_password(self.cleaned_data['password1'])
        
        if user.is_invited_signup_passwd_set_required():  #若是被邀请注册用户重置密码, 则将账号激活
            user.is_active = True
            
        user.save()


class UserInfoUpdateForm(forms.ModelForm):

    gender = forms.CharField(max_length=1, required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserInfoUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('nickname', 'phone', 'gender', 'avatar')

    def clean_avatar(self):
        return None

    def update(self, user):
        user.nickname = self.cleaned_data.get('nickname') or user.nickname
        user.phone = self.cleaned_data.get('phone') or user.phone
        user.gender = self.cleaned_data.get('gender') or user.gender
        
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            #nickname
            pass
        user.save()
