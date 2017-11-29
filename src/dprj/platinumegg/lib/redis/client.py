## -*- coding: utf-8 -*-


import redis
import settings_sub
from platinumegg.lib.redis import config

redis_db_connection_pool = redis.ConnectionPool(host=settings_sub.REDIS_DB_HOST, port=6379, db=settings_sub.REDIS_DB_NUMBER)
redis_cache_connection_pool = redis.ConnectionPool(host=settings_sub.REDIS_CACHE_HOST, port=6379, db=settings_sub.REDIS_CACHE_NUMBER)

connection_pools = {}
for dbname, params in config.databases.items():
    connection_pools[dbname] = redis.ConnectionPool(**params)

class Client:
    
    @staticmethod
    def get(db=config.REDIS_DEFAULT):
        pool = connection_pools.get(db, connection_pools[config.REDIS_DEFAULT])
        client = redis.Redis(connection_pool=pool)
        return client

