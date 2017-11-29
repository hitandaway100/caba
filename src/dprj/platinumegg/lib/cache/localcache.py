# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
import cPickle
import os
import settings_sub
import socket

_local_cache_data = {}

class localcache:
    """
    各フロントエンド毎にデータをキャッシュする.
    マスターデータ等の不変な値はこっちに入れる.
    スケールしてると Web鯖 ⇔ Cache鯖 の通信もオーバーヘッドになるので...
    
    memcache消したら一緒に消えるくらいな感じがいい.
    ＊オブジェクトをそのまま入れるとlocalcache.setしてないのに値が変わったりするのでcPickle.dumpsした値を入れる。
    　（メモリの節約にもなる）
    """
    CHECKED_HOST_LIST_KEY = 'localCacheCheckedHostList'
    
    DEFAULT_NAMESPACE = 'DefaultNameSpace'
    
    class Client:
        def __init__(self):
            self.__cache = _local_cache_data
        def _getCacheData(self):
            return self.__cache
        
        def __to_cachekey(self, key):
            return str(key)
        
        def __get_namespace_group(self, namespace):
            namespace = namespace or localcache.DEFAULT_NAMESPACE
            self.__cache[namespace] = self.__cache.get(namespace) or {}
            return self.__cache[namespace]
        
        def get(self, key, namespace=None):
            if not settings_sub.USE_LOCALCACHE:
                return None
            
            cachekey = self.__to_cachekey(key)
            group = self.__get_namespace_group(namespace)
            
            dump_data = group.get(cachekey, None)
            if dump_data is None:
                return None
            else:
                return cPickle.loads(dump_data)
        
        def set(self, key, value, namespace=None, **kwargs):
            if not settings_sub.USE_LOCALCACHE:
                return
            cachekey = self.__to_cachekey(key)
            group = self.__get_namespace_group(namespace)
            group[cachekey] = cPickle.dumps(value)
        
        def get_many(self, keys, namespace=None):
            ret = {}
            for key in keys:
                aa = self.get(key, namespace=namespace)
                if aa is not None:
                    ret[key] = aa
            return ret
        
        def set_many(self, data, namespace=None, **kwargs):
            for key,value in data.items():
                self.set(key, value, namespace=namespace)
        
        def delete(self, key, namespace=None):
            #一つ消しても他のフロントでデータ残っちゃうので全部消す.
            self.flush()
        
        def delete_many(self, keys, namespace=None):
            #一つ消しても他のフロントでデータ残っちゃうので全部消す.
            self.flush()
        
        def flush(self):
            localcache._resetCacheData()
            key = localcache.CHECKED_HOST_LIST_KEY
            client = OSAUtil.get_cache_client()
            client.delete(key)
    
    @staticmethod
    def initCache():
        client = OSAUtil.get_cache_client()
        
        host = socket.gethostname()
        pid = os.getpid()
        localcache_host = '%s:%s' % (host,pid)
        key = localcache.CHECKED_HOST_LIST_KEY
        host_list = client.get(key)
        do_write_cache = False
        
        if host_list is None:
            host_list = []
            do_write_cache = True
        if localcache_host not in host_list:
            localcache._resetCacheData()
            host_list.append(localcache_host)
            do_write_cache = True
        
        if do_write_cache:
            client.set(key, host_list)
    
    @staticmethod
    def _resetCacheData():
        global _local_cache_data
        _local_cache_data = {}
