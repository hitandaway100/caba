# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel

class PlayerLevelDistributionAmount(KpiModel):
    """レベルごとのプレイヤー数.
    """
    
    @classmethod
    def makeKey(cls):
        return cls.__name__
    
    def __init__(self, uid, level):
        self.uid = uid
        self.level = level
    
    def _save(self, pipe):
        pipe.zadd(self.__class__.makeKey(), self.uid, self.level)
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(), self.uid)
    
    @classmethod
    def aggregate(cls):
        """集計.
        """
        key = cls.makeKey()
        return cls.aggregateSortedSet(key)
