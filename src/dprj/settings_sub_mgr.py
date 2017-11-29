# -*- coding: utf-8 -*-
# This file was made from build.xml.
APP_NAME = 'cabaret'
APP_TITLE = u'キャバ王〜キャストは全員AV女優〜'
APP_TITLE_SHORT = u'キャバ王'
PROJECT_NAME = 'dprj'
WEB_GLOBAL_HOST = '211.11.100.164'
CDN_GLOBAL_HOST = '211.11.100.164'
MEDIA_GLOBAL_HOST = '211.11.100.167'

# MySQL.
MYSQL_DATABASE_NAME = 'cabaret'
MYSQL_WAIT_TIMEOUT = 28800
MYSQL_MASTER_HOST = '10.116.41.100'
MYSQL_SLAVE_HOST = '10.116.41.101'
MYSQL_BACKUP_HOST = '10.116.41.102'
MYSQL_POOL_SIZE = 15
MYSQL_WAIT_TIMEOUT = 28800

# Redis.
REDIS_DB_HOST = '10.116.41.124'
REDIS_DB_NUMBER = 0
REDIS_DB_MAXCONNECTION = 20
REDIS_CACHE_HOST = '10.116.41.126'
REDIS_CACHE_NUMBER = 1
REDIS_CACHE_MAXCONNECTION = 28
REDIS_LOG_HOST = '10.116.41.127'
REDIS_LOG_NUMBER = 2
REDIS_LOG_MAXCONNECTION = 28
REDIS_SESSION_HOST = '10.116.41.126'
REDIS_SESSION_NUMBER = 3
REDIS_SESSION_MAXCONNECTION = 4
REDIS_BATTLEEVENT_HOST = '10.116.41.124'
REDIS_BATTLEEVENT_NUMBER = 4
REDIS_BATTLEEVENT_MAXCONNECTION = 10
REDIS_KPI_HOST = '10.116.41.127'
REDIS_KPI_NUMBER = 5
REDIS_KPI_MAXCONNECTION = 10

MEDIA_DOC_ROOT = '/var/www/html/cabaret_media'
MEDIA_URL_ROOT = 'http://%s/cabaret_media/' % MEDIA_GLOBAL_HOST

STATIC_DOC_ROOT = '/var/www/html/cabaret_static'
STATIC_URL_ROOT = 'http://211.11.100.167/cabaret_static/'

TMP_DOC_ROOT='/var/tmp/cabaret_tmp'
KPI_ROOT = '/var/www/cgi-bin/kpi/cabaret_kpi'

ERR_LOG_PATH = '/var/www/cgi-bin/django_err'

IS_LOCAL = False
IS_DEV = False
IS_BENCH = False
USE_LOG = True

CACHE_BACKEND = 'redis'
USE_LOCALCACHE = True

LAUNCH_MODE = 2

MEDIA_DOWNLOAD_FROM = 'http://10.116.41.12/'
MEDIA_WEBLIST_FILE = '/var/www/cgi-bin/media_weblist'

WOWZA_UPLOAD_HOST = ['10.116.41.80']
WOWZA_CONTENT_ROOT = '/usr/local/WowzaStreamingEngine/content/cabaret_quest'

MASTER_DOWNLOAD_FROM = 'http://10.116.41.12/'

SHELL_SCRIPT_ROOT = '/var/www/cgi-bin/cabaret/tool/upload'

SERVER_PASS = '7sR9#aynbvwzR'

CROSS_PROMOTION = False

LOCAL_PLATFORM = 'dmmsp'