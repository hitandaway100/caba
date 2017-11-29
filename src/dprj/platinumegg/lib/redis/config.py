## -*- coding: utf-8 -*-
import settings_sub

REDIS_DEFAULT = 'default'
REDIS_CACHE = 'cache'
REDIS_LOG = 'log'
REDIS_SESSION = 'session'
REDIS_BATTLEEVENT = 'battleevent'
REDIS_TRADESHOP = 'tradeshop'
REDIS_KPI = 'kpi'

databases = {
            REDIS_DEFAULT : {
                'host':settings_sub.REDIS_DB_HOST,
                'port':6379,
                'db':settings_sub.REDIS_DB_NUMBER,
                'max_connections':settings_sub.REDIS_DB_MAXCONNECTION,
            },
            REDIS_CACHE : {
                'host':settings_sub.REDIS_CACHE_HOST,
                'port':6379,
                'db':settings_sub.REDIS_CACHE_NUMBER,
                'max_connections':settings_sub.REDIS_CACHE_MAXCONNECTION,
            },
            REDIS_LOG : {
                'host':settings_sub.REDIS_LOG_HOST,
                'port':6379,
                'db':settings_sub.REDIS_LOG_NUMBER,
                'max_connections':settings_sub.REDIS_LOG_MAXCONNECTION,
            },
            REDIS_SESSION : {
                'host':settings_sub.REDIS_SESSION_HOST,
                'port':6379,
                'db':settings_sub.REDIS_SESSION_NUMBER,
                'max_connections':settings_sub.REDIS_SESSION_MAXCONNECTION,
            },
            REDIS_BATTLEEVENT : {
                'host':settings_sub.REDIS_BATTLEEVENT_HOST,
                'port':6379,
                'db':settings_sub.REDIS_BATTLEEVENT_NUMBER,
                'max_connections':settings_sub.REDIS_BATTLEEVENT_MAXCONNECTION,
            },
            REDIS_KPI : {
                'host':settings_sub.REDIS_KPI_HOST,
                'port':6379,
                'db':settings_sub.REDIS_KPI_NUMBER,
                'max_connections':settings_sub.REDIS_KPI_MAXCONNECTION,
            },
}
