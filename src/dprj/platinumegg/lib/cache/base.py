# -*- coding: utf-8 -*-

class Client:
    
    def _from_cache_value(self, value):
        return value
    
    def _to_cache_value(self, value):
        return value
    
    def _make_key(self, key, namespace=None):
        return key
    
    def ttl(self, key, time=86400, namespace=None):
        return True
    
    def set(self, key, value, time=86400, namespace=None):
        return True
    
    def get(self, key, namespace=None):
        return None
    
    def incr(self, key, namespace=None, delta=1):
        return delta
    
    def mget(self, keys, namespace=None):
        return {}
    
    def mset(self, datadict, time=0, min_compress_len=0, namespace=None):
        return [True] * len(datadict.keys())
    
    def delete(self, key, namespace=None):
        return True
    
    def mdelete(self, keys, namespace=None):
        return [True] * len(keys)
    
    def flush(self, namespace=None):
        return True
