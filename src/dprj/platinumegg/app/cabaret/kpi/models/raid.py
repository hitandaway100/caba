# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel, DailyKpiModel

class DailyRaidBase(KpiModel):
    """日別レイド集計.
    """
    @classmethod
    def makeKey(cls, date, raidid):
        return '{clsname}##{mid}##{date}'.format(clsname=cls.__name__, mid=raidid, date=DailyKpiModel.datetimeToString(date))
    
    @classmethod
    def incrby(cls, date, raidid, level, v=1, pipe=None):
        key = cls.makeKey(date, raidid)
        def _incr(pipe):
            pipe.hincrby(key, level, v)
        cls.run_in_pipe(_incr, pipe)
    
    @classmethod
    def aggregate(cls, date, raidid):
        """集計.
        """
        redisdb = cls.getDB()
        key = cls.makeKey(date, raidid)
        tmp = redisdb.hgetall(key) or {}
        data = {}
        for k,v in tmp.items():
            try:
                data[long(k)] = int(v)
            except:
                data[k] = int(v)
        return data
    
    @classmethod
    def deleteByDate(cls, raididlist, date, pipe=None):
        redisdb = cls.getDB()
        def delete(pipe, raididlist, date):
            for raidid in raididlist:
                redisdb.delete(cls.makeKey(date, raidid))
        cls.run_in_pipe(delete, pipe, raididlist, date)

class DailyRaidAppearCount(DailyRaidBase):
    """レイド発生回数.
    """

class DailyRaidDestroyCount(DailyRaidBase):
    """レイド討伐数.
    """

