#coding=utf-8
#
# Created on Sep 16, 2014, by Junn
#
from utils import logs

'''消息推送服务

'''

import jpush as jpush
from settings import JPUSH

_jpush = jpush.JPush(JPUSH['app_key'], JPUSH['master_secret'])

def push_to_all(msg):
    '''push system message to all'''
    push = _jpush.create_push()
    push.platform = jpush.all_
    push.audience = jpush.all_
    push.message = jpush.message(content_type=msg.type, msg_content=msg.content, extras=msg.extras)
    
    try:
        push.send()
        logs.debug('Pushed to jpush: \n %s' % msg)
        return True
    except Exception, e:
        logs.warn('push_to_all error: \n %s' % e)    
        return False

def push_to_single(alias, msg):
    '''push to a single user
    
    @param alias:  need to pushed object 
    
    Example:
        msg = PushMessage('R', 'You have new message', extras={'regard': regard.id})
        push_to_single(regard.receiver_id, msg)
    '''
    
    push = _jpush.create_push()
    push.audience = jpush.audience(jpush.alias(alias))
    # jpush之前的版本 msg_content不可以为空, 或空串, 否则无法推送成功
    push.message = jpush.message(content_type=msg.type, msg_content=msg.content, extras=msg.extras)  
    push.platform = jpush.all_
    
    try:
        push.send()
        logs.debug('message pushed to jpush: %s' % msg)
        return True
    except Exception, e:
        logs.warn('push_to_single error: \n %s' % e)    
        return False

def push_to_many(tag, msg):
    push = _jpush.create_push()
    push.platform = jpush.all_
    
    push.send()

        
        