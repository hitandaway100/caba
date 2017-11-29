# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import DailySortedSetKpiModel,\
    KpiModel, DailyHashKpiModel
import cPickle

class BattleEventMemberCount(DailyHashKpiModel):
    """バトルイベントのバトル所属人数.
    """
    
    def __init__(self, date, rank, num):
        DailyHashKpiModel.__init__(self, date)
        self.rank = rank
        self.num = num
    
    def _save(self, pipe):
        pipe.hset(self.key, self.rank, self.num)
    
    def _delete(self, pipe):
        pipe.hdel(self.key, self.rank)

class BattleEventJoin(DailySortedSetKpiModel):
    """バトルイベントのバトル参加数.
    """
    
    def __init__(self, date, uid, rank):
        DailySortedSetKpiModel.__init__(self, date)
        self.uid = uid
        self.rank = rank
    
    def _save(self, pipe):
        pipe.zadd(self.key, self.uid, self.rank)
    
    def _delete(self, pipe):
        pipe.zrem(self.key, self.uid)

class BattleEventResult(DailyHashKpiModel):
    """バトルイベントの結果情報.
    """
    
    def __init__(self, date, uid, rank, grouprank, point):
        DailyHashKpiModel.__init__(self, date)
        self.uid = uid
        self.rank = rank
        self.grouprank = grouprank
        self.point = point
    
    def _save(self, pipe):
        v = cPickle.dumps((self.rank, self.grouprank, self.point))
        pipe.hset(self.key, self.uid, v)
    
    def _delete(self, pipe):
        pipe.hdel(self.key, self.uid)
    
    @staticmethod
    def fetch(date, uidlist):
        redisdb = BattleEventResult.getDB()
        key = BattleEventResult.makeKey(date)
        values = redisdb.hmget(key, uidlist)
        dest = []
        for idx,uid in enumerate(uidlist):
            v = values[idx]
            if v:
                rank, grouprank, point = cPickle.loads(v)
                dest.append(BattleEventResult(date, uid, rank, grouprank, point))
        return dest

class BattleEventFame(KpiModel):
    """バトルイベントのバトル参加数.
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

class BattleEventDailyUserRankSet(DailyHashKpiModel):
    """バトルイベントの日別ランク情報.
    """
    
    def __init__(self, date, uid, rank):
        DailyHashKpiModel.__init__(self, date)
        self.uid = uid
        self.rank = rank
    
    def _save(self, pipe):
        pipe.hset(self.key, self.uid, self.rank)
    
    def _delete(self, pipe):
        pipe.hdel(self.key, self.uid)
    
    @staticmethod
    def fetch(date, uidlist):
        redisdb = BattleEventDailyUserRankSet.getDB()
        key = BattleEventDailyUserRankSet.makeKey(date)
        values = redisdb.hmget(key, uidlist)
        dest = {}
        for idx,uid in enumerate(uidlist):
            v = values[idx]
            if v and str(v).isdigit():
                dest[uid] = int(v)
        return dest

class BattleEventBattleCountBase(DailyHashKpiModel):
    """バトルイベントのバトル回数集計のベース.
    """
    
    def __init__(self, date, uid, cnt):
        DailyHashKpiModel.__init__(self, date)
        self.uid = uid
        self.cnt = cnt
    
    def _save(self, pipe):
        pipe.hset(self.key, self.uid, self.cnt)
    
    def _delete(self, pipe):
        pipe.hdel(self.key, self.uid)
    
    @classmethod
    def fetch(cls, date, uidlist):
        redisdb = cls.getDB()
        key = cls.makeKey(date)
        values = redisdb.hmget(key, uidlist)
        dest = {}
        for idx,uid in enumerate(uidlist):
            v = values[idx]
            if v and str(v).isdigit():
                dest[uid] = int(v)
        return dest

class BattleEventBattleCountAttack(BattleEventBattleCountBase):
    """バトルイベントの攻撃回数.
    """
class BattleEventBattleCountDefense(BattleEventBattleCountBase):
    """バトルイベントの防衛回数.
    """
class BattleEventBattleCountAttackWin(BattleEventBattleCountBase):
    """バトルイベントの攻撃勝利回数.
    """
class BattleEventBattleCountDefenseWin(BattleEventBattleCountBase):
    """バトルイベントの防衛勝利回数.
    """

class BattleEventPieceCollect(DailyHashKpiModel):
    """バトルイベントのピース集計回数.
    RedisのKey: BattleEventPieceCollect##20150718 (後ろは日付)
    HashのKey:  ID + レアリティ (ex, 1R 1SR 2R,....)
    HashのValue:count
    """
    def __init__(self, date, rare):
        DailyHashKpiModel.__init__(self, date)
        self.rare = rare

    def _save(self, pipe):
        pipe.hincrby(self.key, str(self.rare), 1)

    def _delete(self, pipe):
        pipe.hdel(self.key, self.uid)
