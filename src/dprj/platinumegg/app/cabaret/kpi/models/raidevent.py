# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel,DailyKpiModel,\
    EventStageDistributionAmount

class RaidEventSortedSetUserMap(KpiModel):
    """
    """
    @classmethod
    def makeKey(cls, eventid):
        return "%s##%s" % (cls.__name__, eventid)
    
    def __init__(self, eventid, uid, point):
        self.eventid = eventid
        self.uid = uid
        self.point = point
    
    def _save(self, pipe):
        pipe.zadd(self.__class__.makeKey(self.eventid), self.uid, self.point)
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(self.eventid), self.uid)
    
    @classmethod
    def aggregate(cls, eventid):
        """集計.
        """
        return cls.aggregateSortedSet(cls.makeKey(eventid))

class RaidEventDailySortedSetKpiModel(KpiModel):
    """
    """
    @classmethod
    def makeKey(cls, date, eventid):
        return '{clsname}##{date}##{eventid}'.format(clsname=cls.__name__, date=DailyKpiModel.datetimeToString(date), eventid=eventid)
    
    def __init__(self, date, eventid):
        self.date = date
        self.eventid = eventid
    
    @property
    def key(self):
        return self.__class__.makeKey(self.date, self.eventid)
    
    @classmethod
    def deleteByDate(cls, date, eventid, pipe=None):
        def delete(pipe):
            pipe.delete(cls.makeKey(date, eventid))
        cls.run_in_pipe(delete, pipe)
    
    @classmethod
    def aggregate(cls, date, eventid):
        """集計.
        """
        return cls.aggregateSortedSet(cls.makeKey(date, eventid))

class RaidEventPoint(RaidEventSortedSetUserMap):
    """ユーザー毎の秘宝獲得数.
    """

class RaidEventConsumePoint(RaidEventSortedSetUserMap):
    """ユーザー別消費秘宝数.
    """

class RaidEventDailyTicket(RaidEventDailySortedSetKpiModel):
    """日別イベント用チケット交換数.
    """
    def __init__(self, date, eventid, uid, count):
        RaidEventDailySortedSetKpiModel.__init__(self, date, eventid)
        self.uid = uid
        self.count = count
    
    def _save(self, pipe):
        pipe.zadd(self.key, self.uid, self.count)
    
    def _delete(self, pipe):
        pipe.zrem(self.key, self.uid)
    
    @classmethod
    def incrby(cls, date, eventid, uid, count=1, pipe=None):
        key = cls.makeKey(date, eventid)
        def _incr(pipe):
            pipe.zincrby(key, uid, count)
        cls.run_in_pipe(_incr, pipe)
    

class RaidEventDailyConsumeTicket(RaidEventDailySortedSetKpiModel):
    """日別チケット消費数(=イベントガチャ実行数).
    """
    def __init__(self, date, eventid, uid, count):
        RaidEventDailySortedSetKpiModel.__init__(self, date, eventid)
        self.uid = uid
        self.count = count
    
    def _save(self, pipe):
        pipe.zadd(self.key, self.uid, self.count)
    
    def _delete(self, pipe):
        pipe.zrem(self.key, self.uid)
    
    @classmethod
    def incrby(cls, date, eventid, uid, count=1, pipe=None):
        key = cls.makeKey(date, eventid)
        def _incr(pipe):
            pipe.zincrby(key, uid, count)
        cls.run_in_pipe(_incr, pipe)

class RaidEventDestroyUserNum(RaidEventSortedSetUserMap):
    """通常太客討伐回数別ユーザー数.
    """

class RaidEventDestroyUserNumBig(RaidEventSortedSetUserMap):
    """大ボス討伐回数別ユーザー数.
    """

class RaidEventDestroyLevelMap(KpiModel):
    """超太客Lv別討伐回数.
    """
    @classmethod
    def makeKey(cls, eventid, raidid):
        return "%s##%s##%s" % (cls.__name__, eventid, raidid)
    
    @classmethod
    def incrby(cls, eventid, raidid, level, cnt=1, pipe=None):
        key = cls.makeKey(eventid, raidid)
        def _incr(pipe):
            pipe.hincrby(key, level, cnt)
        cls.run_in_pipe(_incr, pipe)
    
    @classmethod
    def deleteByEventID(cls, eventid, raidid, pipe=None):
        key = cls.makeKey(eventid, raidid)
        def _incr(pipe):
            pipe.delete(key)
        cls.run_in_pipe(_incr, pipe)
    
    @classmethod
    def hgetall(cls, eventid, raidid):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid, raidid)
        return redisdb.hgetall(key)

class RaidEventStageDistributionAmount(EventStageDistributionAmount):
    """ステージごとのプレイヤー数.
    """

