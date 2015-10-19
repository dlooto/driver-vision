#coding=utf-8
#
# Created on May 18, 2014, by Junn
#

from django.conf.urls import patterns, url

from runtests import views
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^/qq_login$',  TemplateView.as_view(template_name='auth/qq_login.html')),
    
    url(r'^/send_sms$',  views.SMSView.as_view()),
    
    url(r'^/unread_posts',  views.test_unread_posts),
    url(r'/auth_token',     views.TestView.as_view()),
    url(r'^/request_auth',  views.test_request_auth),
    
    url(r'^/jpush$',            views.test_jpush),
    url(r'^/jpush_posts$',      views.test_jpush_posts),
    
    url(r'^/qiniu_upload$',     views.test_qiniu_upload),   #七牛包文件上传
    url(r'^/send_request$',     views.test_send_request),   #发送http请求
    
    url(r'^/load_pic$',         views.test_load_weixin_pic), #请求远程图片文件并存储到本地
)