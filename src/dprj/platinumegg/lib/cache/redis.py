# -*- coding: utf-8 -*-
import pickle
import settings_sub
from platinumegg.lib.cache import base
from platinumegg.lib.redis import config, client

class Client(base.Client):
    
    NAMESPACE_DEFAULT = 'Default'
    
    def __init__(self, db=config.REDIS_CACHE):
        self.__redis = client.Client.get(db)
    
    def _from_cache_value(self, value):
        if value is None:
            return None
        elif str(value).isdigit():
            return value
        else:
            return pickle.loads(value[len('pickle:'):])
    
    def _to_cache_value(self, value):
        if str(value).isdigit():
            return value
        else:
            return 'pickle:'+pickle.dumps(value)
    
    def _valid_namespace(self, namespace=None):
        return namespace or Client.NAMESPACE_DEFAULT
    
    def _make_key(self, key, namespace=None):
        return '%s:%s:%s' % (settings_sub.APP_NAME, self._valid_namespace(namespace), key)
    
    def _mget(self, keys, namespace=None):
        cache_keys = [self._make_key(key, namespace) for key in keys]
        mgetdata = self.__redis.mget(*cache_keys)
        
        result = {}
        for idx, key in enumerate(keys):
            v = self._from_cache_value(mgetdata[idx])
            if v is not None:
                result[key] = v
        return result
    
    def _set(self, key, value, time=86400, namespace=None, pipe=None):
        cache_key = self._make_key(key, namespace)
        mypipe = pipe
        if mypipe is None:
            mypipe = self.__redis.pipeline()
        
        mypipe.set(cache_key, self._to_cache_value(value))
        if 0 < time:
            mypipe.expire(cache_key, time)
        
        if pipe is None:
            return mypipe.execute()
        else:
            return True
    
    def _delete(self, key, namespace=None, pipe=None):
        mypipe = pipe
        if mypipe is None:
            mypipe = self.__redis.pipeline()
        mypipe.delete(self._make_key(key, namespace))
        if pipe is None:
            return mypipe.execute()
        else:
            return True
    
    def ttl(self, key, time=86400, namespace=None):
        cache_key = self._make_key(key, namespace)
        return self.__redis.expire(cache_key, time)
    
    def set(self, key, value, time=86400, namespace=None):
        return self._set(key, value, time, namespace)
    
    def get(self, key, namespace=None):
        result = self._mget([key], namespace)
        return result.get(key, None)
    
    def incr(self, key, namespace=None, delta=1):
        cache_key = self._make_key(key, namespace)
        return self.__redis.incrby(cache_key, delta)
    
    def mget(self, keys, namespace=None):
        return self._mget(keys, namespace)
    
    def mset(self, datadict, time=86400, namespace=None):
        pipe = self.__redis.pipeline()
        for k,v in datadict.items():
            self._set(k, v, time, namespace, pipe)
        return pipe.execute()
    
    def delete(self, key, namespace=None):
        return self._delete(key, namespace)
    
    def mdelete(self, keys, namespace=None):
        pipe = self.__redis.pipeline()
        for key in keys:
            self._delete(key, namespace, pipe)
        return pipe.execute()
    
    def flush(self):
        return self.__redis.flushdb()
