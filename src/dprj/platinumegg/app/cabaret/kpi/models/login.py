# -*- coding: utf-8 -*-
import datetime
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.kpi.models.base import DailySetKpiModel


class WeeklyLoginSet(DailySetKpiModel):
    """過去1週間のログイン
        ソートセット
        キー
            日付
        メンバ
            ユーザID
        バリュー
            SP    1
            PC    2
            両方   3
    """
    @classmethod
    def getDBName(cls):
        return config.REDIS_KPI
    
    def __init__(self, date, uid, is_pc=None):
        DailySetKpiModel.__init__(self, date)
        self.uid = uid
        self.is_pc = is_pc
    
    def _save(self, pipe):
        redisdb = WeeklyLoginSet.getDB()
        v = redisdb.zscore(self.key, self.uid)
        if v:
            v = int(v)
        else:
            v = 0
        if self.is_pc:
            v = v | 2
        else:
            v = v | 1
        pipe.zadd(self.key, self.uid, v)
    
    def _delete(self, pipe):
        pipe.zrem(self.key, self.uid)
    
    @staticmethod
    def getUserIdListByRange(s_time, e_time):
        """ある区間のユーザIDのリストを取得.
        ここで返すユーザIDは文字列です.
        """
        interval = datetime.timedelta(days=1)
        keys = []
        dt = s_time
        while dt <= e_time:
            keys.append(WeeklyLoginSet.makeKey(dt))
            dt += interval
        if not keys:
            return []
        
        redisdb = WeeklyLoginSet.getDB()
        dest_key = '%s:%s' % (WeeklyLoginSet.makeKey(s_time), WeeklyLoginSet.makeKey(e_time))
        redisdb.zunionstore(dest_key, keys)
        redisdb.expire(dest_key, 60)
        
        num = redisdb.zcard(dest_key)
        uidlist = redisdb.zrange(dest_key, 0, num)
        redisdb.delete(dest_key)
        
        return uidlist
    
    @staticmethod
    def countByPlatform(now, sp=True, pc=True):
        """プラットフォームを指定して人数を取得.
        """
        if not sp and not pc:
            return 0
        
        redisdb = WeeklyLoginSet.getDB()
        key = WeeklyLoginSet.makeKey(now)
        v = (int(bool(sp)) * 1) | (int(bool(pc)) * 2)
        return redisdb.zcount(key, v, v)
