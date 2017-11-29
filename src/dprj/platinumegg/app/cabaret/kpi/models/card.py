# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel, DailyKpiModel
from platinumegg.lib.redis import config

class CardDistributionAmount(KpiModel):
    """カードの流通量.
    """
    
    @classmethod
    def makeKey(cls):
        return cls.__name__
    
    def __init__(self, cardid, mid):
        self.cardid = cardid
        self.mid = mid
    
    def _save(self, pipe):
        pipe.zadd(self.__class__.makeKey(), self.cardid, self.mid)
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(), self.cardid)
    
    @classmethod
    def aggregate(cls):
        """集計.
        """
        key = cls.makeKey()
        return cls.aggregateSortedSet(key)

class RingGetNumHash(KpiModel):
    """日別のユーザ別指輪獲得数
    ハッシュ型
        キー
            日付+mid
        メンバ
            ユーザID+入手先
        バリュー
            獲得数
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    @classmethod
    def makeKey(cls, date, mid):
        return '%s##%s#%s' % (cls.__name__, DailyKpiModel.datetimeToString(date), mid)
    
    @classmethod
    def makeMember(cls, uid, way):
        return '%s#%s' % (uid, way)
    
    def __init__(self, uid, mid, way, date, cnt=0):
        self.uid = uid
        self.date = date
        self.mid = mid
        self.way = way
        self.cnt = cnt
    
    def _save(self, pipe):
        pipe.hset(self.__class__.makeKey(self.date, self.mid), self.makeMember(self.uid, self.way), self.cnt)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.makeKey(self.date, self.mid), self.makeMember(self.uid, self.way))
    
    @classmethod
    def incrby(cls, uid, mid, way, date, cnt=0, pipe=None):
        """獲得数をインクリメント.
        """
        key = cls.makeKey(date, mid)
        member = cls.makeMember(uid, way)
        def _incr(pipe):
            pipe.hincrby(key, member, cnt)
        cls.run_in_pipe(_incr, pipe)

