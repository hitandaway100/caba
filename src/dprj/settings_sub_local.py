# -*- coding: utf-8 -*-
# This file was made from build.xml.
APP_NAME = 'cabaret'
APP_TITLE = u'キャバ王?キャストは全?AV女??'
APP_TITLE_SHORT = u'キャバ王'
PROJECT_NAME = 'dprj'
WEB_GLOBAL_HOST = '127.0.0.1:8080'
CDN_GLOBAL_HOST = '127.0.0.1:8080'
MEDIA_GLOBAL_HOST = WEB_GLOBAL_HOST

# MySQL.
MYSQL_DATABASE_NAME = 'cabaret'
MYSQL_WAIT_TIMEOUT = 28800
MYSQL_MASTER_HOST = '127.0.0.1'
MYSQL_SLAVE_HOST = '127.0.0.1'
MYSQL_POOL_SIZE = 5
MYSQL_WAIT_TIMEOUT = 28800

# Redis.
REDIS_DB_HOST = '127.0.0.1'
REDIS_DB_NUMBER = 0
REDIS_DB_MAXCONNECTION = 5
REDIS_CACHE_HOST = '127.0.0.1'
REDIS_CACHE_NUMBER = 1
REDIS_CACHE_MAXCONNECTION = 5
REDIS_LOG_HOST = '127.0.0.1'
REDIS_LOG_NUMBER = 2
REDIS_LOG_MAXCONNECTION = 5
REDIS_SESSION_HOST = '127.0.0.1'
REDIS_SESSION_NUMBER = 3
REDIS_SESSION_MAXCONNECTION = 5
REDIS_BATTLEEVENT_HOST = '127.0.0.1'
REDIS_BATTLEEVENT_NUMBER = 4
REDIS_BATTLEEVENT_MAXCONNECTION = 5
REDIS_KPI_HOST = '127.0.0.1'
REDIS_KPI_NUMBER = 5
REDIS_KPI_MAXCONNECTION = 5

MEDIA_DOC_ROOT = '/Users/jinliu/Documents/workMMd/CabaretQuest/media'
MEDIA_URL_ROOT = 'http://127.0.0.1:8080/cabaret_media/'

STATIC_DOC_ROOT = '/Users/jinliu/Documents/workMMd/CabaretQuest/static'
STATIC_URL_ROOT = 'http://127.0.0.1:8080/cabaret_static/'

TMP_DOC_ROOT = '/Users/jinliu/Documents/workMMd/CabaretQuest/tmp'
KPI_ROOT = '/Users/jinliu/Documents/workMMd/CabaretQuest/tmp/kpi'

ERR_LOG_PATH = '/Users/jinliu/Documents/workMMd/CabaretQuest/log'

IS_LOCAL = True
IS_DEV = True
IS_BENCH = False
USE_LOG = True

CACHE_BACKEND = 'redis'
USE_LOCALCACHE = True

LAUNCH_MODE = 0

MEDIA_DOWNLOAD_FROM = None
MEDIA_WEBLIST_FILE = None

MASTER_DOWNLOAD_FROM = None

WOWZA_HOST = 'localhost'
WOWZA_PORT = '1935'

SHELL_SCRIPT_ROOT = '/Users/jinliu/Documents/workMMd/CabaretQuest/tool/upload'

SERVER_PASS = None

CROSS_PROMOTION = False

LOCAL_PLATFORM = 'dmmpc'
