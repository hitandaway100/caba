# -*- coding: utf-8 -*-
# This file was made from build.xml.
APP_NAME = 'cabaret'
APP_TITLE = u'キャバ王〜キャストは全員AV女優〜'
APP_TITLE_SHORT = u'キャバ王'
PROJECT_NAME = 'dprj'
WEB_GLOBAL_HOST = '211.130.152.227'
CDN_GLOBAL_HOST = '211.130.152.227'
MEDIA_GLOBAL_HOST = WEB_GLOBAL_HOST

# MySQL.
MYSQL_DATABASE_NAME = 'cabaret'
MYSQL_WAIT_TIMEOUT = 28800
MYSQL_MASTER_HOST = '127.0.0.1'
MYSQL_SLAVE_HOST = '127.0.0.1'
MYSQL_POOL_SIZE = 15
MYSQL_WAIT_TIMEOUT = 28800

# Redis.
REDIS_DB_HOST = '127.0.0.1'
REDIS_DB_NUMBER = 0
REDIS_DB_MAXCONNECTION = 40
REDIS_CACHE_HOST = '127.0.0.1'
REDIS_CACHE_NUMBER = 1
REDIS_CACHE_MAXCONNECTION = 50
REDIS_LOG_HOST = '127.0.0.1'
REDIS_LOG_NUMBER = 2
REDIS_LOG_MAXCONNECTION = 50
REDIS_SESSION_HOST = '127.0.0.1'
REDIS_SESSION_NUMBER = 3
REDIS_SESSION_MAXCONNECTION = 50
REDIS_BATTLEEVENT_HOST = '127.0.0.1'
REDIS_BATTLEEVENT_NUMBER = 4
REDIS_BATTLEEVENT_MAXCONNECTION = 10
REDIS_KPI_HOST = '127.0.0.1'
REDIS_KPI_NUMBER = 5
REDIS_KPI_MAXCONNECTION = 10

MEDIA_DOC_ROOT = '/var/www/html/cabaret_media'
MEDIA_URL_ROOT = 'http://%s/cabaret_media/' % MEDIA_GLOBAL_HOST

STATIC_DOC_ROOT = '/var/www/html/cabaret_static'
STATIC_URL_ROOT = 'http://211.130.152.227/cabaret_static/'

TMP_DOC_ROOT='/var/tmp/cabaret_tmp'
KPI_ROOT = '/var/www/cgi-bin/kpi/cabaret_kpi'

ERR_LOG_PATH = '/var/www/cgi-bin/django_err'

IS_LOCAL = False
IS_DEV = True
IS_BENCH = False
USE_LOG = True

CACHE_BACKEND = 'redis'
USE_LOCALCACHE = True

LAUNCH_MODE = 0

MEDIA_DOWNLOAD_FROM = None
MEDIA_WEBLIST_FILE = None

WOWZA_HOST = '535f30bd57ac2.streamlock.net'
WOWZA_PORT = '1935'
WOWZA_UPLOAD_HOST = '10.116.41.98'
WOWZA_CONTENT_ROOT = '/usr/local/WowzaStreamingEngine/content/cabaret_quest'

MASTER_DOWNLOAD_FROM = None

SHELL_SCRIPT_ROOT = '/var/www/cgi-bin/cabaret/tool/upload'

SERVER_PASS = None

CROSS_PROMOTION = True

LOCAL_PLATFORM = 'dmmsp'
