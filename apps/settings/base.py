#coding=utf-8## Created on 2014-3-21, by junn###############################################################         Server Base settings############################################################import osPROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))DEBUG = FalseTEMPLATE_DEBUG = DEBUGADMINS = (    # ('Your Name', 'your_email@example.com'),)MANAGERS = ADMINSDATABASES = {    "default": {        "ENGINE": 'django.db.backends.mysql', # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".        "NAME": 'vision',                 # Or path to database file if using sqlite3.        "USER": 'root',                       # Not used with sqlite3.        "PASSWORD": 'root',                 # Not used with sqlite3.        "HOST": 'localhost',                  # Set to empty string for localhost. Not used with sqlite3.        "PORT": '3306',                       # Set to empty string for default. Not used with sqlite3.    }}### Redis # Note: ``LOCATION`` needs to be host:port:db_id# CACHES = {#     'default': {#         'BACKEND': 'redis_cache.cache.RedisCache',#         'LOCATION': '127.0.0.1:6379:0',#         'OPTIONS': {#             'CLIENT_CLASS': 'redis_cache.client.DefaultClient',#             'CONNECTION_POOL_KWARGS': {'max_connections': 100}#         },#     },# }## Every write to the cache will also be written to the database, # Session reads only use the database if the data is not already in the cache.# this setting depends on CACHES setup    #SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"# For this type session cache, Session data will be stored directly your cache, # and session data may not be persistentSESSION_ENGINE = "django.contrib.sessions.backends.cache"SESSION_CACHE_ALIAS = 'default'# Hosts/domain names that are valid for this site; required if DEBUG is False# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hostsALLOWED_HOSTS = []AUTH_USER_MODEL = 'users.User'# Local time zone for this installation. Choices can be found here:# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name# although not all choices may be available on all operating systems.# In a Windows environment this must be set to your system time zone.TIME_ZONE = 'Asia/Shanghai'# Language code for this installation. All choices can be found here:# http://www.i18nguy.com/unicode/language-identifiers.htmlLANGUAGE_CODE = 'zh-cn'SITE_ID = 1# If you set this to False, Django will make some optimizations so as not# to load the internationalization machinery.USE_I18N = True# If you set this to False, Django will not format dates, numbers and# calendars according to the current locale.USE_L10N = True# If you set this to False, Django will not use timezone-aware datetimes.USE_TZ = False# Absolute filesystem path to the directory that will hold user-uploaded files.MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')MEDIA_URL = '/media/'STATIC_URL = '/static/'############# 以下设置为相对路径# 用户头像设置USER_DEFAULT_AVATAR = 'user_avatar_default1.jpg'# 用户头像存放目录USER_AVATAR_DIR = {    'original': 'img/avatar/originals',    'thumb':    'img/avatar/thumbs'}# 其他图片存放目录IMG_DIR = {    'original': 'img/originals',    #原图目录    'thumb':    'img/thumbs',       #缩略图目录         }AUD_DIR = 'aud'DEFAULT_THUMB_SIZE = (400, 400)     #默认缩略图尺寸配置# Additional locations of static filesSTATICFILES_DIRS = (    # Put strings here, like "/home/html/static" or "C:/www/django/static".    # Always use forward slashes, even on Windows.    # Don't forget to use absolute paths, not relative paths.        ("vision", os.path.join(STATIC_ROOT, 'vision')),  # Just added for local debug env)# List of finder classes that know how to find static files in# various locations.STATICFILES_FINDERS = (    'django.contrib.staticfiles.finders.FileSystemFinder',    'django.contrib.staticfiles.finders.AppDirectoriesFinder',    )    # Make this unique, and don't share it with anybody.SECRET_KEY = '$^0#lv$kycl5!d-hq0yp*wsx90oyt90n'# List of callables that know how to import templates from various sources.TEMPLATE_LOADERS = (    'django.template.loaders.filesystem.Loader',    'django.template.loaders.app_directories.Loader',)MIDDLEWARE_CLASSES = [    'django.middleware.common.CommonMiddleware',    'django.contrib.sessions.middleware.SessionMiddleware',    'django.middleware.csrf.CsrfViewMiddleware',    'django.contrib.auth.middleware.AuthenticationMiddleware',    'django.contrib.messages.middleware.MessageMiddleware',    ]ROOT_URLCONF = 'urls'TEMPLATE_DIRS = (    os.path.join(PROJECT_ROOT, 'templates'),)TEMPLATE_CONTEXT_PROCESSORS = [    "django.contrib.auth.context_processors.auth",    "django.core.context_processors.debug",    "django.core.context_processors.i18n",    "django.core.context_processors.static",    "django.core.context_processors.media",    "django.core.context_processors.request",    'django.core.context_processors.csrf',    'django.contrib.messages.context_processors.messages',          # mambaby    #"core.context_processors.import_settings",    ]INSTALLED_APPS = [    'django.contrib.auth',    'django.contrib.contenttypes',    'django.contrib.sessions',    'django.contrib.sites',    'django.contrib.messages',    'django.contrib.staticfiles',        'suit',    #'widget_tweaks',    'django.contrib.admin',         # django admin    "debug_toolbar",        #'djcelery',    #'django_crontab',    'core',    'utils',    'auth',    'users',    'vision', ]FIXTURE_DIRS = [    os.path.join(PROJECT_ROOT, "resources"),]# django-suit settingsSUIT_CONFIG = {    'ADMIN_NAME' :          '视觉测试管理后台',        'HEADER_DATE_FORMAT':   'Y年m月d日 H:i',  #'l, jS F Y',    'HEADER_TIME_FORMAT':   '-------------------------',}# 设置admin的默认时间显示格式DATE_FORMAT = 'Y-m-d'DATETIME_FORMAT = 'Y-m-d H:i:s'CSRF_FAILURE_VIEW = 'core.views.csrf_failure'try:    from log_settings import *except ImportError:    pass