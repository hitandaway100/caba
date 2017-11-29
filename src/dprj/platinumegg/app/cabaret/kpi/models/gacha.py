# -*- coding: utf-8 -*-
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.kpi.models.base import DailySetKpiModel, KpiModel
import cPickle
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import time
from platinumegg.lib import timezone


class GachaLastStepSortSet(KpiModel):
    """最後にプレイしたステップ数.
        セット
        キー
            日付+マスターID
        メンバ
            ユーザID
        バリュー
            ステップ数
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    @classmethod
    def makeKey(cls, date, mid):
        return '{clsname}##{mid}##{date}'.format(clsname=cls.__name__, mid=mid, date=DailySetKpiModel.datetimeToString(date))
    
    def __init__(self, date, uid, mid, step=None):
        self.date = date
        self.uid = uid
        self.mid = mid
        self.step = step
    
    def _save(self, pipe):
        pipe.zadd(self.makeKey(self.date, self.mid), self.uid, self.step)
    
    def _delete(self, pipe):
        pipe.zrem(self.makeKey(self.date, self.mid), self.uid)
    
    @staticmethod
    def getStep(date, mid, uid):
        """ある日のあるユーザの最後にプレイしたステップ数を取得.
        """
        redisdb = GachaLastStepSortSet.getDB()
        return redisdb.zscore(GachaLastStepSortSet.makeKey(date, mid), uid)

class PaymentGachaPlayerLeaderHash(KpiModel):
    """課金ガチャ(期間限定のみ)を回したユーザーのリーダーカード情報.
    ハッシュ型
        キー
            固定
        メンバ
            ユーザID
        値
            生涯課金額
            {
                直近で引いたガチャID(boxID?) : {
                    'card':ガチャを引いた時のリーダー,
                    'date':ガチャを引いた時間,
                },
            } * 3
    """
    RECORD_NUM_MAX = 2
    
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    def __init__(self, uid, gachaid, leadercard_mid, now=None):
        self.uid = uid
        self.gachaid = gachaid
        self.leadercard_mid = leadercard_mid
        self.now = now or OSAUtil.get_now()
    
    def _save(self, pipe):
        redisdb = self.getDB()
        strdata = redisdb.hget(self.__class__.__name__, self.uid)
        data = None
        if strdata:
            try:
                data = cPickle.loads(strdata)
                if not isinstance(data, dict):
                    data = None
            except:
                pass
        data = data or {}
        str_now = DateTimeUtil.dateTimeToStr(self.now)
        if data.has_key(self.gachaid):
            data[self.gachaid]['date'] = str_now
        else:
            items = list(data.items())
            if self.__class__.RECORD_NUM_MAX <= len(items):
                # レコードの最大数を超えている.
                items.sort(key=lambda x:x[1]['date'])
                data = dict(items[1:])
            data[self.gachaid] = {
                'card' : self.leadercard_mid,
                'date' : str_now,
            }
        strdata = cPickle.dumps(data)
        pipe.hset(self.__class__.__name__, self.uid, strdata)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.__name__, self.uid)
    
    @classmethod
    def getByUserIDList(cls, uidlist):
        redisdb = cls.getDB()
        strdata_list = redisdb.hmget(cls.__name__, uidlist)
        
        result = {}
        for idx,uid in enumerate(uidlist):
            strdata = strdata_list[idx]
            data = None
            if strdata:
                try:
                    data = cPickle.loads(strdata)
                    if not isinstance(data, dict):
                        data = None
                except:
                    pass
            if not data:
                continue
            result[uid] = data
        return result

class PaymentGachaLastPlayTimeSortedSet(KpiModel):
    """課金ガチャ(期間限定のみ)を最後に回した時間.
    ソート済みセット
        キー
            固定
        メンバ
            ユーザID
        値
            引いた時間
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    def __init__(self, uid, now=None):
        self.uid = uid
        self.now = now or OSAUtil.get_now()
    
    def _save(self, pipe):
        dbdate = self.now.astimezone(timezone.TZ_DB).replace(tzinfo=None)
        v = int(time.mktime(dbdate.timetuple()))
        pipe.zadd(self.__class__.__name__, self.uid, v)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.__name__, self.uid)
    
    @classmethod
    def fetchByDate(cls, date_from, date_to):
        """日付で絞り込み.
        """
        redisdb = cls.getDB()
        key = cls.__name__
        
        time_from = int(time.mktime(date_from.astimezone(timezone.TZ_DB).replace(tzinfo=None).timetuple()))
        time_to = int(time.mktime(date_to.astimezone(timezone.TZ_DB).replace(tzinfo=None).timetuple()))
        
        str_uidlist = redisdb.zrangebyscore(key, time_from, time_to)
        
        return [int(str_uid) for str_uid in str_uidlist]

