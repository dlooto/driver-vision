#coding=utf-8
#
# Copyright (C) 2015  24Hours TECH Co., Ltd. All rights reserved.
# Created on Aug 10, 2013, by junn
#
#


def get_err_msgs(serializer):
    '''
    Return serializer validation errors messages
    '''
    msg = 'validation error'
    for key in serializer.fields.keys():
        errkey = serializer.errors.get(key)
        if errkey:
            msg = '%s,%s:%s' % (msg, key, errkey[0])

    return msg
