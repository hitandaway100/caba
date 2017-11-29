# -*- coding: utf-8 -*-
import datetime
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.kpi.models.base import DailySetKpiModel, KpiModel,\
    DailySortedSetKpiModel


class FQ5PaymentSet(KpiModel):
    """FQ5
        連続ログインが5以上の課金ユーザー数
        セット
        キー
            日付+マスターID
        メンバ
            ユーザID
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    @classmethod
    def makeKey(cls, date, mid):
        return '{clsname}##{mid}##{date}'.format(clsname=cls.__name__, mid=mid, date=DailySetKpiModel.datetimeToString(date))
    
    def __init__(self, date, uid, mid):
        self.date = date
        self.uid = uid
        self.mid = mid
    
    def _save(self, pipe):
        pipe.sadd(self.makeKey(self.date, self.mid), self.uid)
    
    def _delete(self, pipe):
        pipe.srem(self.makeKey(self.date, self.mid), self.uid)
    
    @staticmethod
    def count(date, mid):
        """ある日のFQ5課金ユーザ数を取得.
        """
        redisdb = FQ5PaymentSet.getDB()
        return redisdb.scard(FQ5PaymentSet.makeKey(date, mid))
    
    @staticmethod
    def countByRange(s_time, e_time, mid):
        """ある期間のFQ5課金ユーザ数を取得.
        """
        interval = datetime.timedelta(days=1)
        keys = []
        dt = s_time
        while dt <= e_time:
            keys.append(FQ5PaymentSet.makeKey(dt, mid))
            dt += interval
        if not keys:
            return 0
        
        redisdb = FQ5PaymentSet.getDB()
        dest_key = '%s:%s' % (FQ5PaymentSet.makeKey(s_time, mid), FQ5PaymentSet.makeKey(e_time, mid))
        redisdb.sunionstore(dest_key, keys)
        
        cnt = redisdb.scard(dest_key)
        
        redisdb.delete(dest_key)
        
        return cnt

class DailyPaymentPointSet(DailySortedSetKpiModel):
    """日別課金額
    ソートセット
        キー
            日付
        メンバ
            ユーザID
        バリュー
            課金額
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    def __init__(self, date, uid, point=0):
        DailySortedSetKpiModel.__init__(self, date)
        self.uid = uid
        self.point = point
    
    @classmethod
    def incrby(cls, uid, date, point=0, pipe=None):
        """消費ポイントをインクリメント.
        """
        key = cls.makeKey(date)
        def _incr(pipe):
            pipe.zincrby(key, uid, point)
        cls.run_in_pipe(_incr, pipe)
    
    @classmethod
    def makeUnionSortSet(cls, s_time, e_time):
        """一定期間のunionを作成.
        """
        interval = datetime.timedelta(days=1)
        keys = []
        dt = s_time
        while dt <= e_time:
            keys.append(cls.makeKey(dt))
            dt += interval
        if not keys:
            return 0
        
        redisdb = cls.getDB()
        dest_key = '%s:%s' % (cls.makeKey(s_time), cls.makeKey(e_time))
        redisdb.zunionstore(dest_key, keys)
        
        return dest_key
