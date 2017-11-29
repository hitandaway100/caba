# -*- coding: utf-8 -*-
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class KpiModel():
    """KPIデータのモデル.
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_LOG
    
    @classmethod
    def getDB(cls):
        return Client.get(cls.getDBName())
    
    @classmethod
    def create(cls, *args, **kwargs):
        ins = cls(*args, **kwargs)
        return ins
    
    def validate(self):
        return None
    
    def _save(self, pipe):
        raise NotImplementedError
    
    def _delete(self, pipe):
        raise NotImplementedError
    
    @classmethod
    def run_in_pipe(cls, func, pipe, *args):
        if pipe is None:
            redisdb = cls.getDB()
            pipe = redisdb.pipeline()
            func(pipe, *args)
            pipe.execute()
        else:
            func(pipe, *args)
    
    def save(self, pipe=None):
        errmessage = self.validate()
        if errmessage:
            raise CabaretError('%s:%s' % (self.__class__.__name__, errmessage))
        else:
            self.run_in_pipe(self._save, pipe)
    
    def delete(self, pipe=None):
        self.run_in_pipe(self._delete, pipe)
    
    @classmethod
    def aggregateSortedSet(cls, key):
        """SortedSetの集計.
        """
        data = {}
        
        redisdb = cls.getDB()
        
        arr = redisdb.zrevrange(key, 0, 0, withscores=True, score_cast_func=long)
        if not arr:
            return None
        
        _, score = arr[0]
        while True:
            num = redisdb.zcount(key, score, score)
            data[score] = num
            arr = redisdb.zrevrangebyscore(key, score - 1, 0, start=0, num=1, withscores=True, score_cast_func=long)
            if not arr:
                break
            _, score = arr[0]
        return data

class DailyKpiModel(KpiModel):
    """日毎集計のKPI.
    """
    
    @classmethod
    def datetimeToString(cls, date):
        return date.strftime("%Y%m%d")
    
    @classmethod
    def makeKey(cls, date):
        return '{clsname}##{date}'.format(clsname=cls.__name__, date=cls.datetimeToString(date))
    
    def __init__(self, date):
        self.date = date
    
    @property
    def key(self):
        return self.__class__.makeKey(self.date)
    
    @classmethod
    def deleteByDate(cls, date, pipe=None):
        def delete(pipe):
            pipe.delete(cls.makeKey(date))
        cls.run_in_pipe(delete, pipe)
    

class DailySetKpiModel(DailyKpiModel):
    """日毎集計のKPI(Set).
    """
    def __init__(self, date, *args, **kwargs):
        DailyKpiModel.__init__(self, date)
    
    @classmethod
    def aggregate(cls, date):
        """集計.
        """
        key = cls.makeKey(date)
        redisdb = cls.getDB()
        return redisdb.scard(key)

class DailySortedSetKpiModel(DailyKpiModel):
    """日毎集計のKPI(SortedSet).
    """
    def __init__(self, date, *args, **kwargs):
        DailyKpiModel.__init__(self, date)
    
    @classmethod
    def aggregate(cls, date):
        """集計.
        """
        key = cls.makeKey(date)
        return cls.aggregateSortedSet(key)

class DailyHashKpiModel(DailyKpiModel):
    """日毎集計のKPI(Hash).
    """
    def __init__(self, date, *args, **kwargs):
        DailyKpiModel.__init__(self, date)
    
    @classmethod
    def incrby(cls, date, member, v=1, pipe=None):
        key = cls.makeKey(date)
        def _incr(pipe):
            pipe.hincrby(key, member, v)
        cls.run_in_pipe(_incr, pipe)
    
    @classmethod
    def aggregate(cls, date):
        """集計.
        """
        redisdb = cls.getDB()
        key = cls.makeKey(date)
        tmp = redisdb.hgetall(key) or {}
        data = {}
        for k,v in tmp.items():
            try:
                data[long(k)] = v
            except:
                data[k] = v
        return data

class EventStageDistributionAmount(KpiModel):
    """イベントスカウトのステージごとのプレイヤー数.
    """
    
    @classmethod
    def makeKey(cls, eventid):
        return cls.__name__
    
    def __init__(self, eventid, uid, stage):
        self.eventid = eventid
        self.uid = uid
        self.stage = stage
    
    def _save(self, pipe):
        pipe.zadd(self.__class__.makeKey(self.eventid), self.uid, self.stage)
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(self.eventid), self.uid)
    
    @classmethod
    def aggregate(cls, eventid):
        """集計.
        """
        key = cls.makeKey(eventid)
        return cls.aggregateSortedSet(key)

