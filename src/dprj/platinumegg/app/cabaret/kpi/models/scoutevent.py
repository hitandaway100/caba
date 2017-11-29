# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel,\
    EventStageDistributionAmount


class ScoutEventStageDistributionAmount(EventStageDistributionAmount):
    """ステージごとのプレイヤー数.
    """

class ScoutEventPointSet(KpiModel):
    """各プレイヤーの獲得ポイント.
    """
    
    @classmethod
    def makeKey(cls, eventid):
        return cls.__name__
    
    def __init__(self, eventid, uid, point):
        self.eventid = eventid
        self.uid = uid
        self.point = point
    
    def _save(self, pipe):
        pipe.hset(self.__class__.makeKey(self.eventid), self.uid, self.point)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.makeKey(self.eventid), self.uid)
    
    @classmethod
    def aggregate(cls, eventid):
        """集計.
        """
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        tmp = redisdb.hgetall(key) or {}
        data = {}
        for k,v in tmp.items():
            try:
                data[long(k)] = v
            except:
                data[k] = v
        return data

class ScoutEventGachaPointConsumeHash(KpiModel):
    """各プレイヤーの消費ガチャポイント.
    """
    
    @classmethod
    def makeKey(cls, eventid):
        return cls.__name__
    
    def __init__(self, eventid, uid, point):
        self.eventid = eventid
        self.uid = uid
        self.point = point
    
    def _save(self, pipe):
        pipe.hset(self.__class__.makeKey(self.eventid), self.uid, self.point)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.makeKey(self.eventid), self.uid)
    
    @classmethod
    def incrby(cls, eventid, uid, point):
        def write(pipe, key, uid, point):
            pipe.hincrby(key, uid, point)
        cls.run_in_pipe(write, None, cls.makeKey(eventid), uid, point)
    
    @classmethod
    def aggregate(cls, eventid):
        """集計.
        """
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        tmp = redisdb.hgetall(key) or {}
        data = {}
        for k,v in tmp.items():
            try:
                data[long(k)] = v
            except:
                data[k] = v
        return data

class ScoutEventTipConsumeHash(KpiModel):
    """消費したチップ数.
    """
    @classmethod
    def makeKey(cls, uid):
        return '{}#{}'.format(cls.__name__, uid)
    
    def __init__(self, uid, number, tanzaku):
        self.uid = uid
        self.number = number
        self.tanzaku = tanzaku
    
    def _save(self, pipe):
        pipe.hset(self.__class__.makeKey(self.uid), self.number, self.tanzaku)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.makeKey(self.uid), self.number)
    
    @classmethod
    def incrby(cls, uid, number, tanzaku):
        def write(pipe, key, number, tanzaku):
            pipe.hincrby(key, number, tanzaku)
        cls.run_in_pipe(write, None, cls.makeKey(uid), number, tanzaku)
    
    @classmethod
    def aggregate(cls, uid_max):
        """集計.
        ユーザID,キャスト0,キャスト1,キャスト2,キャスト3,キャスト4
        """
        redisdb = cls.getDB()
        
        data = []
        for uid in xrange(1, uid_max+1):
            key = cls.makeKey(uid)
            if not redisdb.exists(key):
                continue
            
            tmp = list((redisdb.hgetall(key) or {}).items())
            arr = range(5)
            for number,tanzaku in tmp:
                arr[int(number)] = tanzaku
            data.append([uid] + arr)
        
        return data

class ScoutEventTanzakuHash(KpiModel):
    """取得した短冊数.
    """
    
    @classmethod
    def makeKey(cls, uid):
        return '{}#{}'.format(cls.__name__, uid)
    
    def __init__(self, uid, number, tanzaku):
        self.uid = uid
        self.number = number
        self.tanzaku = tanzaku
    
    def _save(self, pipe):
        pipe.hset(self.__class__.makeKey(self.uid), self.number, self.tanzaku)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.makeKey(self.uid), self.number)
    
    @classmethod
    def incrby(cls, uid, number, tanzaku):
        def write(pipe, key, number, tanzaku):
            pipe.hincrby(key, number, tanzaku)
        cls.run_in_pipe(write, None, cls.makeKey(uid), number, tanzaku)
    
    @classmethod
    def aggregate(cls, uid_max):
        """集計.
        ユーザID,短冊0,短冊1,短冊2,短冊3,短冊4
        """
        redisdb = cls.getDB()
        
        data = []
        for uid in xrange(1, uid_max+1):
            key = cls.makeKey(uid)
            if not redisdb.exists(key):
                continue
            
            tmp = list((redisdb.hgetall(key) or {}).items())
            arr = range(5)
            for number,tanzaku in tmp:
                arr[int(number)] = tanzaku
            data.append([uid] + arr)
        
        return data
