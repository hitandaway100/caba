# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel
from platinumegg.lib.redis import config


class EventUUDaily(KpiModel):
    """日別イベントUU.
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    @classmethod
    def makeKey(cls, date, is_pc):
        return '%s##%s##%s' % (cls.__name__, date.strftime("%Y%m%d"), int(bool(is_pc)))
    
    def __init__(self, date, uid, is_pc):
        self.date = date
        self.uid = uid
        self.is_pc = is_pc
    
    def _save(self, pipe):
        pipe.sadd(self.makeKey(self.date, self.is_pc), self.uid)
    
    def _delete(self, pipe):
        pipe.srem(self.makeKey(self.date, self.is_pc), self.uid)

class EventPaymentPointDaily(KpiModel):
    """日別消費ポイント.
    """
    
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    @classmethod
    def makeKey(cls, date, is_pc):
        return '%s##%s##%s' % (cls.__name__, date.strftime("%Y%m"), int(bool(is_pc)))
    
    @classmethod
    def incrby(cls, date, point, is_pc, pipe=None):
        key = cls.makeKey(date, is_pc)
        member = date.day
        def _incr(pipe):
            pipe.hincrby(key, member, point)
        cls.run_in_pipe(_incr, pipe)
    
    def __init__(self, date, is_pc, point=0):
        self.date = date
        self.point = 0
        self.is_pc = is_pc
    
    def _save(self, pipe):
        pipe.hset(self.makeKey(self.date, self.is_pc), self.date.day, self.point)
    
    def _delete(self, pipe):
        pipe.hdel(self.makeKey(self.date, self.is_pc), self.date.day)

class EventJoinDaily(EventUUDaily):
    """日別イベント参加数.
    イベントTOPとルール説明を見たUU.
    """
    def __init__(self, date, uid, is_pc):
        EventUUDaily.__init__(self, date, uid, is_pc)

class EventPlayDaily(EventUUDaily):
    """日別イベントプレイ数.
    イベントポイントを自分で稼いだユーザ数.
    """
    def __init__(self, date, uid, is_pc):
        EventUUDaily.__init__(self, date, uid, is_pc)

class EventGachaPaymentUUDaily(EventUUDaily):
    """日別イベントガチャプレイ数.
    """
    def __init__(self, date, uid, is_pc):
        EventUUDaily.__init__(self, date, uid, is_pc)

class EventShopPaymentUUDaily(EventUUDaily):
    """日別イベントショップ購入数.
    """
    def __init__(self, date, uid, is_pc):
        EventUUDaily.__init__(self, date, uid, is_pc)

class EventGachaPaymentPointDaily(EventPaymentPointDaily):
    """日別イベントガチャ消費ポイント.
    """
    def __init__(self, date, is_pc, point=0):
        EventPaymentPointDaily.__init__(self, date, is_pc, point)

class EventShopPaymentPointDaily(EventPaymentPointDaily):
    """日別イベントショップ消費ポイント.
    """
    def __init__(self, date, is_pc, point=0):
        EventPaymentPointDaily.__init__(self, date, is_pc, point)
