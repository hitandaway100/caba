# -*- coding: utf-8 -*-
import cPickle
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventBattleLog
from platinumegg.app.cabaret.util.redisdb import RedisModel, GameLogListBase
import random
import math

class RedisBattleEvent(RedisModel):
    """redis用モデル.
    """
    @classmethod
    def getDB(cls):
        return Client.get(config.REDIS_BATTLEEVENT)

class BattleEventOppList(RedisBattleEvent):
    """バトルイベントの対戦相手リスト.
    """
    uid=None
    opplist = None
    
    @staticmethod
    def makeKey(uid):
        return 'BattleEventOppList##%s' % uid
    
    @staticmethod
    def create(uid, opplist=None):
        ins = BattleEventOppList()
        ins.uid = RedisBattleEvent.value_to_int(uid)
        ins.opplist = opplist or []
        return ins
    
    @staticmethod
    def get(uid):
        redisdb = RedisBattleEvent.getDB()
        arr = redisdb.smembers(BattleEventOppList.makeKey(uid)) or []
        opplist = []
        for s in arr:
            oid = RedisBattleEvent.value_to_int(s)
            if oid:
                opplist.append(oid)
        if opplist:
            return BattleEventOppList.create(uid, opplist)
        else:
            return None
    
    @staticmethod
    def exists(uid):
        return BattleEventOppList.get(uid) is not None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.opplist is None or not isinstance(self.opplist, list):
            return 'Invalid opplist.'
        return None
    
    def _save(self, pipe):
        pipe.delete(BattleEventOppList.makeKey(self.uid))
        pipe.sadd(BattleEventOppList.makeKey(self.uid), *self.opplist)
    
    def _delete(self, pipe):
        pipe.delete(BattleEventOppList.makeKey(self.uid))

class BattleEventOppRivalListCost(RedisModel):
    """バトルイベントのライバル対戦相手リスト(コスト).
    """
    KEY = 'BattleEventOppRivalListCost'
    uid=None
    deckcost=None
    @classmethod
    def create(cls, uid, deckcost):
        ins = cls()
        ins.uid = uid
        ins.deckcost = deckcost
        return ins
    
    @classmethod
    def fetch_by_cost(cls, cost, lower=0, upper=0, limit=100, ignorelist=None):
        ignorelist = ignorelist or []
        redisdb = RedisModel.getDB()
        datalist = list(redisdb.zrangebyscore(cls.KEY, cost, cost, withscores=True))
        not_enough = limit - len(datalist)
        if 0 < not_enough:
            if 1 < cost and 0 < lower:
                datalist.extend(redisdb.zrevrangebyscore(cls.KEY, cost-1, max(1, cost-lower), start=0, num=not_enough, withscores=True))
            if 0 < upper:
                datalist.extend(redisdb.zrangebyscore(cls.KEY, cost+1, cost+lower, start=0, num=not_enough, withscores=True))
            datalist.sort(key=lambda x:math.fabs(cost - x[1]))
        dest = []
        for str_uid, _ in datalist:
            uid = cls.value_to_int(str_uid)
            if (not uid) or (uid in ignorelist):
                continue
            dest.append(uid)
            if limit <= len(dest):
                break
        return dest
    
    def _save(self, pipe):
        pipe.zadd(self.KEY, self.uid, self.deckcost)
        pipe.expire(self.KEY, 21600)
    
    def _delete(self, pipe):
        pipe.zrem(self.KEY, self.uid)

class BattleEventOppRivalList(RedisModel):
    """バトルイベントのライバル対戦相手リスト.
    """
    KEY = 'BattleEventOppRivalList'
    uid=None
    deckcost=None
    ltime=None
    userdict={}

    @classmethod
    def create(cls, uid, deckcost, ltime):
        ins = cls()
        ins.uid = uid
        ins.deckcost = deckcost
        ins.ltime = ltime
        ins.userdict = cls.get()
        return ins

    @classmethod
    def get(cls):
        redisdb = RedisModel.getDB()
        userdict = redisdb.get(cls.KEY)
        if userdict:
            return cPickle.loads(userdict)
        else:
            return {}

    def update(self):
        redisdb = RedisModel.getDB()
        userdict = self.get()
        data = {
            self.uid: {
                'deckcost': self.deckcost,
                'ltime': self.ltime
            }
        }
        userdict.update(data)
        redisdb.set(self.KEY, cPickle.dumps(userdict))
        redisdb.expire(self.KEY, 21600)

class BattleEventBattleLogListSet(GameLogListBase):
    """バトルイベントの行動履歴.
    """
    @classmethod
    def getDB(cls):
        return Client.get(config.REDIS_BATTLEEVENT)
    
    @classmethod
    def get_modelclass(cls):
        return BattleEventBattleLog
    
    @staticmethod
    def get_num(uid):
        redisdb = BattleEventBattleLogListSet.getDB()
        key = BattleEventBattleLogListSet.makeKey(uid)
        if not redisdb.exists(key):
            return None
        return redisdb.zcard(key)

class BattleEventRevengeSet(RedisBattleEvent):
    """バトルイベントのリベンジリスト.
    """
    uid=None
    revengeid = None
    
    @staticmethod
    def makeKey(uid):
        return 'BattleEventRevengeSet##%s' % uid
    
    @staticmethod
    def create(uid, revengeid=None):
        ins = BattleEventRevengeSet()
        ins.uid = RedisBattleEvent.value_to_int(uid)
        ins.revengeid = RedisBattleEvent.value_to_int(revengeid)
        return ins
    
    @staticmethod
    def fetchRandom(uid, num):
        redisdb = RedisBattleEvent.getDB()
        arr = redisdb.srandmember(BattleEventRevengeSet.makeKey(uid), num)
        revengeidlist = []
        for s in arr:
            oid = RedisBattleEvent.value_to_int(s)
            if oid:
                revengeidlist.append(oid)
        return revengeidlist
    
    @staticmethod
    def exists(uid):
        redisdb = RedisBattleEvent.getDB()
        return redisdb.scard(BattleEventRevengeSet.makeKey(uid))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.revengeid is None:
            return 'Invalid revengeid.'
        return None
    
    def _save(self, pipe):
        pipe.sadd(BattleEventRevengeSet.makeKey(self.uid), self.revengeid)
    
    def _delete(self, pipe):
        pipe.srem(BattleEventRevengeSet.makeKey(self.uid), self.revengeid)

class BattleEventRankUidSet(RedisBattleEvent):
    """バトルイベントのランクセット.
    """
    eventid=None
    rank=None
    uid=None
    level=None
    
    @staticmethod
    def makeKey(eventid, rank):
        return 'BattleEventRankUidSet##%s##%s' % (eventid, rank)
    
    @staticmethod
    def create(eventid, rank, uid, level=None):
        ins = BattleEventRankUidSet()
        ins.eventid = RedisBattleEvent.value_to_int(eventid)
        ins.uid = RedisBattleEvent.value_to_int(uid)
        ins.rank = RedisBattleEvent.value_to_int(rank)
        ins.level = RedisBattleEvent.value_to_int(level)
        return ins
    
    @staticmethod
    def fetchRandomAll(eventid, rank, num, ignore=None):
        """全体からランダムで取得.
        """
        ignore = ignore or []
        
        redisdb = RedisBattleEvent.getDB()
        key = BattleEventRankUidSet.makeKey(eventid, rank)
        
        limit = num + len(ignore)
        targetnummax = redisdb.zcard(key)
        if targetnummax == 0:
            return []
        elif targetnummax <= limit:
            arr = redisdb.zrange(key, 0, targetnummax)
            random.shuffle(arr)
        else:
            LOOP_NUM = 3
            interval = int(targetnummax / LOOP_NUM)
            fraction = targetnummax % LOOP_NUM
            randmax = interval - limit + fraction
            
            # 適当に3回ほど取得してその中から選んでみる.
            tmp = []
            offset = 0
            for _ in xrange(LOOP_NUM):
                frac = int(1 < fraction)
                fraction -= 1
                
                rand_v = random.randint(0, randmax+frac) if 0 < (randmax+frac) else 0
                tmp_offset = offset + rand_v
                uidlist = redisdb.zrange(key, tmp_offset, tmp_offset+limit) or []
                random.shuffle(uidlist)
                tmp.extend(dict(enumerate(uidlist)).items())
                offset += interval+frac
            tmp.sort(key=lambda x:(int(x[0])<<32)+int(x[1]), reverse=True)
            tmp = tmp[:limit]
            arr = [v for _,v in tmp]
            random.shuffle(arr)
        
        dest = []
        for v in arr:
            uid = RedisBattleEvent.value_to_int(v)
            if uid in ignore:
                continue
            dest.append(uid)
        return dest[:num]
    
    @staticmethod
    def fetchRandom(eventid, rank, user_id, num, ignore=None):
        ignore = ignore or []
        
        redisdb = RedisBattleEvent.getDB()
        key = BattleEventRankUidSet.makeKey(eventid, rank)
        
        limit = num + len(ignore)
        index = redisdb.zrank(key, user_id)
        # とりあえず None の時の応急処置
        if index is None:
            index = 100
        saferange = 100

        arr = redisdb.zrange(key, max(0,index-saferange), index+saferange)
        if limit-1 < len(arr):
            arr = random.sample(arr, limit-1)
        dest = []
        for v in arr:
            uid = RedisBattleEvent.value_to_int(v)
            if uid in ignore:
                continue
            dest.append(uid)
        return dest[:num]
    
    @staticmethod
    def exists(eventid, rank):
        redisdb = RedisBattleEvent.getDB()
        return redisdb.exists(BattleEventRankUidSet.makeKey(eventid, rank))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.eventid is None:
            return 'Invalid eventid.'
        elif self.rank is None:
            return 'Invalid rank.'
        elif self.level is None:
            return 'Invalid level.'
        return None
    
    def _save(self, pipe):
        pipe.zadd(BattleEventRankUidSet.makeKey(self.eventid, self.rank), self.uid, self.level)
    
    def _delete(self, pipe):
        pipe.zrem(BattleEventRankUidSet.makeKey(self.eventid, self.rank), self.uid)

def delete_by_user(player):
    """ユーザID指定で削除.
    """
    redisdb = RedisBattleEvent.getDB()
    pipe = redisdb.pipeline()
    
    for key in redisdb.keys('BattleEventRankUidSet##*'):
        pipe.zrem(key, player.id)
    
    pipe.delete(BattleEventRevengeSet.makeKey(player.id))
    pipe.delete(BattleEventBattleLogListSet.makeKey(player.id))
    pipe.delete(BattleEventOppList.makeKey(player.id))
    
    pipe.execute()
