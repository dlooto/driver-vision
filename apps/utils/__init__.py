# __author__ = 'Junn'
# 
# import settings
# import hashlib
# import urllib
# import json
# 
# from des import DES
# 
# 
# def get_sig(s, salt):
#     return hashlib.md5('%s%s' % (s, salt)).hexdigest().upper()
# 
# 
# class API(object):
#     def __init__(self, secret_key=settings.SECRET_KEY, url='/api', key=settings.KEY):
#         self.secret_key = secret_key
#         self.url = url
#         self.key = key
#         #self.domain = settings.UAUTH_DOMAIN   # user center domain
# 
#     def send_request(self, act, data={}):
#         data['app'] = self.key
#         data['act'] = act
#         url = '%s?%s' % (self.url, '&'.join(['%s=%s' % (k, urllib.quote(str(v).encode('utf8'))) for k, v in data.items()]))
#         print url
#         sig = get_sig(url, self.secret_key)
#         url = '%s&sig=%s' % (url, sig)
#         url = '%s%s' % (self.domain, url)
#         try:
#             rs = urllib.urlopen(url)
#             print url
#             result = json.loads(rs.read())
#             return result
#         except Exception, e:
#             return None
# 
# 
# if __name__ == '__main__':
#     api = API()
#     des = DES('abcd1234abcd1234abcd1234abcd1234')
#     password = des.encode('222222')
#     #print api.send_request('register', {'username': 'jingyang.tom2@qq.com', 'password': password})
#     print api.send_request('change_password', {'id': 4, 'password': password})
