# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings_sub
import redis
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class Command(BaseCommand):
    """Redisのデータを移行する.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'migrate_redisdata'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        # どこから.
        if settings_sub.IS_LOCAL:
            from_host = '127.0.0.1'
            from_db = 0
        else:
            from_host = '10.116.41.122'
            from_db = 0
        # どこへ.
        to_host = settings_sub.REDIS_KPI_HOST
        to_db = settings_sub.REDIS_KPI_NUMBER
        # redisクライアント.
        client_from = redis.Redis(host=from_host, port=6379, db=from_db)
        client_to = redis.Redis(host=to_host, port=6379, db=to_db)
        # 移行元のkeyを全て取得.
        key_list = client_from.keys()
        errors = []
        for key in key_list:
            # データの型を取得.
            data_type = client_from.type(key)
            print '{}...{}'.format(key, data_type)
            # 型ごとの処理を実行.
            f = getattr(self, 'migrate_{}'.format(data_type), None)
            if f is None:
                continue
            if not f(client_from, client_to, key):
                errors.append('{}...{}'.format(key, data_type))
                continue
            # keyの有効期限を取得.
            ttl = client_from.ttl(key)
            if 0 < ttl:
                # keyの有効期限を設定.
                client_to.expire(key, ttl)
        
        print '================================'
        print 'all done..'
        print 'error : {}'.format(len(errors))
        if errors:
            for err in errors:
                print '    {}'.format(err)
    
    def migrate_string(self, client_from, client_to, key):
        '@type client_from: redis.Redis'
        '@type client_to: redis.Redis'
        '@type key: string'
        """文字列型データの移行.
        """
        v = client_from.get(key)
        client_to.set(key, v)
        return client_to.get(key) == v
    
    def migrate_list(self, client_from, client_to, key):
        '@type client_from: redis.Redis'
        '@type client_to: redis.Redis'
        '@type key: string'
        """リスト型データの移行.
        """
        length = client_from.llen(key)
        values = client_from.lrange(key, 0, length - 1)
        client_to.rpush(key, *values)
        return client_to.llen(key) == length and client_to.lrange(key, 0, length - 1) == values
    
    def migrate_set(self, client_from, client_to, key):
        '@type client_from: redis.Redis'
        '@type client_to: redis.Redis'
        '@type key: string'
        """セット型データの移行.
        """
        members = client_from.smembers(key)
        client_to.sadd(key, *members)
        return client_to.smembers(key) == members
    
    def migrate_zset(self, client_from, client_to, key):
        '@type client_from: redis.Redis'
        '@type client_to: redis.Redis'
        '@type key: string'
        """ソート済みセット型データの移行.
        """
        cnt = client_from.zcard(key)
        start = 0
        while start < cnt:
            end = min(cnt, start + 10000)
            scores = dict(client_from.zrange(key, start, end, withscores=True))
            client_to.zadd(key, **scores)
            start = end + 1
        if client_to.zcard(key) == cnt:
            return client_from.zrange(key, 0, cnt, withscores=True) == client_to.zrange(key, 0, cnt, withscores=True)
        return False
    
    def migrate_hash(self, client_from, client_to, key):
        '@type client_from: redis.Redis'
        '@type client_to: redis.Redis'
        '@type key: string'
        """ハッシュ型データの移行.
        """
        mapping = client_from.hgetall(key)
        client_to.hmset(key, mapping)
        return mapping == client_to.hgetall(key)
